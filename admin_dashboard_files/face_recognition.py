import cv2
import customtkinter as ctk
import threading
import os
import sys
import json
import numpy as np
from datetime import datetime
from PIL import Image

# PATH FIX for modular DB
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Dummy DB functions if not available
try:
    from db import get_connection, get_student_by_regno, record_attendance
except:
    get_student_by_regno = lambda x: None
    record_attendance = lambda **k: None

from admin_dashboard_files import shared
from admin_dashboard_files.shared import (
    switch_camera_live,
    current_camera_index,
    start_camera_stream,
    present_student_ids,
    present_details_list,
    sidebar_stats_callback
)

# ---------------- Recognition Globals ----------------
CLASSIFIER_PATH = os.path.join(parent_dir, "classifier.xml")
LABEL_MAP_PATH  = os.path.join(parent_dir, "models", "label_map.json")

# Haar cascades
face_xml = os.path.join(parent_dir, "cascade/haarcascade_frontalface_default.xml")
if not os.path.exists(face_xml):
    face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_xml)
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

recognizer = cv2.face.LBPHFaceRecognizer_create()
model_loaded = False
label_map = {}

# --- Unknown Capture Tracking ---
import time
UNKNOWN_SESSION_ID = None
UNKNOWN_CAPTURE_COUNT = 0
LAST_UNKNOWN_SEEN_TIME = 0
LAST_CAPTURE_TIME = 0

def handle_unknown_capture(frame, x, y, w, h):
    global UNKNOWN_SESSION_ID, UNKNOWN_CAPTURE_COUNT, LAST_UNKNOWN_SEEN_TIME, LAST_CAPTURE_TIME
    
    current_time = time.time()
    
    # If it's been more than 5 seconds since the last unknown face, start a new session
    if current_time - LAST_UNKNOWN_SEEN_TIME > 5:
        UNKNOWN_SESSION_ID = "unk_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        UNKNOWN_CAPTURE_COUNT = 0
        LAST_CAPTURE_TIME = 0
        
    LAST_UNKNOWN_SEEN_TIME = current_time
    
    # Capture up to 5 images, maximum 1 image every 0.6 seconds
    if UNKNOWN_CAPTURE_COUNT < 5 and (current_time - LAST_CAPTURE_TIME > 0.6):
        try:
            unknown_dir = os.path.join(parent_dir, "unknowns", UNKNOWN_SESSION_ID)
            os.makedirs(unknown_dir, exist_ok=True)
            
            # Save the cropped face with a little padding
            pad = 30
            y1 = max(0, y - pad)
            y2 = min(frame.shape[0], y + h + pad)
            x1 = max(0, x - pad)
            x2 = min(frame.shape[1], x + w + pad)
            
            face_img = frame[y1:y2, x1:x2]
            
            if face_img.size > 0:
                img_path = os.path.join(unknown_dir, f"capture_{UNKNOWN_CAPTURE_COUNT+1}.jpg")
                cv2.imwrite(img_path, face_img)
                UNKNOWN_CAPTURE_COUNT += 1
                LAST_CAPTURE_TIME = current_time
        except Exception as e:
            print(f"Failed to save unknown image: {e}")

# ---------------- Utility Functions ----------------
def load_label_map():
    global label_map
    try:
        if os.path.exists(LABEL_MAP_PATH):
            with open(LABEL_MAP_PATH, "r") as f:
                label_map = json.load(f)
    except:
        label_map = {}

def reload_classifier():
    global recognizer, model_loaded
    try:
        if os.path.exists(CLASSIFIER_PATH):
            recognizer.read(CLASSIFIER_PATH)
            model_loaded = True
            return True
    except:
        pass
    return False

load_label_map()
reload_classifier()

# Cache for student details
STUDENT_DETAILS_CACHE = {}
def get_cached_student(sid):
    if sid in STUDENT_DETAILS_CACHE:
        return STUDENT_DETAILS_CACHE[sid]
    rec = get_student_by_regno(sid)
    if rec:
        info = {
            "full_name": rec.get("full_name", sid),
            "course": rec.get("course", "N/A"),
            "session": rec.get("session", "N/A"),
            "department": rec.get("department", "N/A")
        }
        STUDENT_DETAILS_CACHE[sid] = info
        return info
    return None

# Enhance grayscale image (Consistent with training)
def enhance_face(img_gray):
    denoised = cv2.GaussianBlur(img_gray, (3, 3), 0)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    clahe_img = clahe.apply(denoised)
    norm = cv2.equalizeHist(clahe_img)
    blur = cv2.GaussianBlur(norm, (0, 0), 1)
    sharp = cv2.addWeighted(norm, 1.2, blur, -0.2, 0)
    return sharp

# Align face using eyes (optional)
def align_face(img_gray, face_box):
    x, y, w, h = face_box
    roi_gray = img_gray[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.3, minNeighbors=8, minSize=(30, 30))
    
    if len(eyes) >= 2:
        eyes = sorted(eyes, key=lambda e: e[0])
        lex, ley, lw, lh = eyes[0]
        rex, rey, rw, rh = eyes[-1]
        l_center = (x + lex + lw//2, y + ley + lh//2)
        r_center = (x + rex + rw//2, y + rey + rh//2)
        dy = r_center[1] - l_center[1]
        dx = r_center[0] - l_center[0]
        angle = float(np.degrees(np.arctan2(dy, dx)))
        center = (float((l_center[0] + r_center[0]) / 2), float((l_center[1] + r_center[1]) / 2))
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        aligned = cv2.warpAffine(img_gray, M, (img_gray.shape[1], img_gray.shape[0]), flags=cv2.INTER_LINEAR)
        return aligned, (l_center, r_center)
    return img_gray, None

# Draw label on frame
def draw_label(img, text, org, font, scale, txt_color, bg_color, thickness=1):
    (tw, th), bl = cv2.getTextSize(text, font, scale, thickness)
    px, py = max(1, int(6*scale)), max(1, int(4*scale))
    x0, y0 = max(0, int(org[0])-px), max(0, int(org[1])-th-py)
    x1, y1 = min(img.shape[1], int(org[0])+tw+px), min(img.shape[0], int(org[1])+bl+py)
    cv2.rectangle(img, (x0, y0), (x1, y1), bg_color, -1)
    cv2.putText(img, text, (int(org[0]), int(org[1])), font, scale, txt_color, thickness, cv2.LINE_AA)

FONT = cv2.FONT_HERSHEY_SIMPLEX

# ---------------- Face Recognition Frame ----------------
def get_recognition_frame():
    global model_loaded
    if shared.camera_cap is None or not shared.camera_cap.isOpened():
        return None, []
    ret, frame = shared.camera_cap.read()
    if not ret:
        return None, []

    gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Increased minNeighbors (from 6 to 9) to heavily penalize false positives.
    # Increased minSize (from 60 to 80) to ignore small background textures.
    faces = face_cascade.detectMultiScale(gray_full, scaleFactor=1.3, minNeighbors=6, minSize=(40, 40))
    print("Faces detected:", len(faces))
    detections = []

    for (x, y, w, h) in faces:
        name, reg_no, course, session = "Unknown", "", "", ""
        box_color, bg_color = (0, 0, 255), (0, 0, 200) # Red for Unknown
        font_scale = max(0.45, min(0.7, w/150.0)) # Slightly larger text for readability
        
        aligned_gray, eye_points = align_face(gray_full, (x, y, w, h))

        if model_loaded:
            try:
                # Crop exact face box
                face_roi = aligned_gray[y:y+h, x:x+w]

                if face_roi.size > 0:
                    roi_resize = cv2.resize(face_roi, (100, 100))  # Match training
                    roi_r = enhance_face(roi_resize)

                    lbl, conf = recognizer.predict(roi_r)
                    
                    # LOWER threshold means STRICTER AI. 
                    # 105 ensures that loose matches are rejected and marked as "Unknown".
                    confidence_threshold = 85
                    if conf < confidence_threshold:
                        sid = label_map.get(str(lbl), "Unknown")
                        if sid != "Unknown":
                            student_info = get_cached_student(sid)
                            if student_info:
                                name = student_info["full_name"]
                                course = student_info["course"]
                                session = student_info["session"]
                                dept = student_info["department"]
                                box_color = (0, 255, 0) # Green for recognized
                                bg_color = (0, 180, 0) # Darker Green BG for name
                                reg_no = sid

                                # Mark attendance once
                                if sid not in shared.present_student_ids:
                                    shared.present_student_ids.add(sid)
                                    now = datetime.now()
                                    shared.present_details_list.append({
                                        'name': name,
                                        'reg': sid,
                                        'course': course,
                                        'session': session,
                                        'date': now.strftime("%Y-%m-%d"),
                                        'time': now.strftime("%H:%M:%S")
                                    })

                                    threading.Thread(target=record_attendance, kwargs={
                                        'reg_no': sid,
                                        'name': name,
                                        'course': course,
                                        'program': session,
                                        'department': dept,
                                        'status': "Present"
                                    }, daemon=True).start()

                                    if shared.sidebar_stats_callback:
                                        shared.sidebar_stats_callback()

                                detections.append({
                                    "reg_no": sid,
                                    "name": name,
                                    "course": course,
                                    "session": session
                                })
                            else:
                                # Not in the database system at all
                                name = "Unknown"
                                box_color = (0, 0, 255)
                                bg_color = (0, 0, 200)
                                handle_unknown_capture(frame, x, y, w, h)
                        else:
                            # Not in label map
                            name = "Unknown"
                            box_color = (0, 0, 255)
                            bg_color = (0, 0, 200)
                            handle_unknown_capture(frame, x, y, w, h)
                    else:
                        # Confidence too low
                        name = "Unknown"
                        box_color = (0, 0, 255)
                        bg_color = (0, 0, 200)
                        handle_unknown_capture(frame, x, y, w, h)

            except Exception as e:
                print(f"Recognition Error: {e}")

        # Draw face box with thicker modern corners
        cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
        L = int(w * 0.15) # Corner length
        t = 4             # Corner thickness
        cv2.line(frame, (x, y), (x+L, y), box_color, t)
        cv2.line(frame, (x, y), (x, y+L), box_color, t)
        cv2.line(frame, (x+w, y), (x+w-L, y), box_color, t)
        cv2.line(frame, (x+w, y), (x+w, y+L), box_color, t)
        cv2.line(frame, (x, y+h), (x+L, y+h), box_color, t)
        cv2.line(frame, (x, y+h), (x, y+h-L), box_color, t)
        cv2.line(frame, (x+w, y+h), (x+w-L, y+h), box_color, t)
        cv2.line(frame, (x+w, y+h), (x+w, y+h-L), box_color, t)

        # Draw High-Contrast Labels
        # 1. Main Name Tag (Top)
        draw_label(frame, name, (x, y - 10), FONT, font_scale, (255, 255, 255), bg_color, thickness=2)
        
        # 2. Details Tags (Bottom) - Dark grey background, vibrant neon text
        info_bg = (30, 30, 30)
        start_y = y + h + 25
        spacing = max(22, int(25 * (font_scale/0.5))) # scale spacing slightly
        
        if reg_no: 
            draw_label(frame, f"ID: {reg_no}", (x, start_y), FONT, font_scale*0.85, (0, 255, 255), info_bg, thickness=1) # Neon Yellow
            start_y += spacing
        if course: 
            draw_label(frame, course, (x, start_y), FONT, font_scale*0.85, (255, 200, 0), info_bg, thickness=1) # Neon Sky Blue
            start_y += spacing
        if session and session != "N/A": 
            draw_label(frame, f"Session: {session}", (x, start_y), FONT, font_scale*0.85, (150, 255, 150), info_bg, thickness=1) # Neon Mint Green

    return frame, detections

# ---------------- GUI ----------------
def show_face_recognition_content(content_area, responsive_manager):
    # Ensure the model is loaded every time the tab is opened
    load_label_map()
    reload_classifier()
    
    ctk.CTkLabel(content_area, text="Face Recognition", font=("Segoe UI",28,"bold"), text_color="#3b9dd8").pack(anchor="w", padx=30, pady=(30,10))
    
    # Camera selector
    cam_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    cam_bar.pack(fill="x", padx=30, pady=(0,8))
    ctk.CTkLabel(cam_bar, text="📷 Camera:", font=("Arial",12,"bold"), text_color="gray").pack(side="left", padx=(15,8), pady=8)
    
    cam_btn_refs = {}
    def select_camera(idx):
        switch_camera_live(idx)
        placeholder.configure(text="Switching camera...")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        for i,b in cam_btn_refs.items():
            b.configure(fg_color="#3b9dd8" if i==idx else "#333333")
        threading.Thread(target=lambda: start_camera_stream(idx), daemon=True).start()
    
    for cam_idx in [0,1]:  # laptop + external
        is_avail = cam_idx in shared.available_camera_indices
        btn_text = "Cam 1" if cam_idx==0 else "Cam 0"
        
        b = ctk.CTkButton(cam_bar, text=btn_text, width=100, height=32,
            font=("Arial",10,"bold") if is_avail else ("Arial",9),
            fg_color="#3b9dd8" if cam_idx==current_camera_index else "#333333",
            text_color="black" if is_avail else "#666666",
            state="normal" if is_avail else "disabled",
            hover_color="#2a8cc7", corner_radius=6,
            command=lambda i=cam_idx: select_camera(i)
        )
        b.pack(side="left", padx=4, pady=8)
        cam_btn_refs[cam_idx] = b
    
    # Camera viewport
    camera_card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    camera_card.pack(fill="both", expand=True, padx=30, pady=(0,20))
    viewport = ctk.CTkLabel(camera_card, text="", fg_color="black", height=450, corner_radius=10)
    viewport.pack(fill="both", expand=True, padx=15, pady=15)
    
    placeholder = ctk.CTkLabel(viewport, text="Initializing Camera...", text_color="#666666", font=("Arial",18,"bold"))
    placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    loop_active = [True]
    def on_stop(): loop_active[0]=False
    content_area.stop_camera_loop = on_stop
    
    # Update frames
    def update_frame():
        if not loop_active[0]: return
        try:
            if shared.camera_cap is None or not shared.camera_cap.isOpened():
                placeholder.place(relx=0.5, rely=0.5, anchor="center")
                if loop_active[0] and content_area.winfo_exists():
                    viewport.after(200, update_frame)
                return
            frame, detections = get_recognition_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2.resize(frame_rgb,(640,480)))
                ctk_img = ctk.CTkImage(light_image=img,dark_image=img,size=(640,480))
                viewport.configure(image=ctk_img)
                viewport.image = ctk_img
                if placeholder.winfo_ismapped():
                    placeholder.place_forget()
        except Exception as e:
            print(f"Camera Loop Error: {e}")
        if loop_active[0] and content_area.winfo_exists():
            viewport.after(33, update_frame)
    
    threading.Thread(target=lambda: start_camera_stream(current_camera_index), daemon=True).start()
    update_frame()

def train_all_students_bg(progress_callback, status_callback, done_callback, error_callback):
    """
    Scans train_images/ for all .npy files, trains a combined LBPH model,
    and updates the label map.
    """
    try:
        data_dir_base = os.path.join(parent_dir, "train_images")
        if not os.path.isdir(data_dir_base):
            error_callback("train_images folder not found.")
            return

        student_files = [f for f in os.listdir(data_dir_base) if f.endswith(".npy")]
        if not student_files:
            error_callback("No student data (.npy) found in train_images.")
            return

        faces, ids = [], []
        new_label_map = {}
        total_students = len(student_files)
        total_images_processed = 0

        for idx, filename in enumerate(student_files):
            student_id = filename[:-4] # Remove .npy
            status_callback(f"Training student {idx+1}/{total_students}: {student_id}")
            file_path = os.path.join(data_dir_base, filename)
            
            numeric_label = abs(hash(student_id)) % 100000
            new_label_map[str(numeric_label)] = student_id
            
            try:
                data = np.load(file_path)
                num_imgs = len(data)
                for i, row in enumerate(data):
                    try:
                        # Reshape back to 100x100 grayscale
                        img_np = row.reshape((100, 100)).astype("uint8")
                        # Apply same enhancement as recognition
                        processed_face = enhance_face(img_np)
                        faces.append(processed_face)
                        ids.append(numeric_label)
                        total_images_processed += 1
                    except:
                        continue
                    if i % 10 == 0 or i == num_imgs - 1:
                        current_p = (idx / total_students) + ((i + 1) / num_imgs / total_students)
                        progress_callback(current_p, f"Processed {total_images_processed} images...")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue

        if not faces:
            error_callback("No valid data found to train.")
            return

        status_callback("Saving combined model...")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces, np.array(ids))
        clf.save(CLASSIFIER_PATH)
        
        os.makedirs(os.path.dirname(LABEL_MAP_PATH), exist_ok=True)
        with open(LABEL_MAP_PATH, "w") as f:
            json.dump(new_label_map, f, indent=2)
            
        reload_classifier()
        load_label_map()
        done_callback(total_students, total_images_processed)
    except Exception as e:
        error_callback(str(e))