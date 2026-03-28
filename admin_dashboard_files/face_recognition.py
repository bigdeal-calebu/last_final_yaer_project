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
CLASSIFIER_PATH = os.path.join(parent_dir, "models", "embeddings.pkl")

# OpenCV YuNet Face Detector
yunet_path = os.path.join(parent_dir, "dnn_model", "face_detection_yunet.onnx")
try:
    yunet = cv2.FaceDetectorYN.create(yunet_path, "", (320, 320))
except Exception as e:
    print(f"Error loading YuNet model: {e}")
    yunet = None

# OpenCV SFace (Deep Learning Embeddings)
sface_path = os.path.join(parent_dir, "dnn_model", "face_recognition_sface.onnx")
try:
    sface = cv2.FaceRecognizerSF.create(sface_path, "")
except Exception as e:
    print(f"Error loading SFace model: {e}")
    sface = None

model_loaded = False
embeddings_db = {}

# ---------------- Utility Functions ----------------
def reload_classifier():
    global embeddings_db, model_loaded
    import pickle
    try:
        if os.path.exists(CLASSIFIER_PATH):
            with open(CLASSIFIER_PATH, "rb") as f:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=DeprecationWarning)
                    embeddings_db = pickle.load(f)
            model_loaded = True if len(embeddings_db) > 0 else False
            return True
    except:
        pass
    return False

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

# Dummy DB functions if not available

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

    h_img, w_img = frame.shape[:2]
    gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = []
    
    if yunet is not None:
        yunet.setInputSize((w_img, h_img))
        _, yunet_faces = yunet.detect(frame)
        
        if yunet_faces is not None:
            for face_data in yunet_faces:
                box = face_data[0:4].astype("int")
                (startX, startY, w, h) = box
                
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w_img - 1, startX + w)
                endY = min(h_img - 1, startY + h)
                
                w = endX - startX
                h = endY - startY
                
                if w > 40 and h > 40:
                    faces.append((startX, startY, w, h, face_data))

    print("Faces detected:", len(faces))
    detections = []

    for (x, y, w, h, face_data_arr) in faces:
        name, reg_no, course, session = "Unknown", "", "", ""
        box_color, bg_color = (0, 0, 255), (0, 0, 200) # Red for Unknown
        font_scale = max(0.45, min(0.7, w/150.0)) # Slightly larger text for readability
        
        if model_loaded and sface is not None:
            try:
                # SFace physically aligns the face using the 5 YuNet landmarks for 100% precision
                aligned_crop = sface.alignCrop(frame, face_data_arr)

                if aligned_crop is not None:
                    # Extract live 128D feature directly from the aligned crop
                    live_feature = sface.feature(aligned_crop)
                    
                    best_match = "Unknown"
                    best_score = -1.0
                    
                    # Compute Cosine Similarity distance against all registered students
                    for sid, db_feature in embeddings_db.items():
                        try:
                            # Verify shapes beforehand to avoid crash
                            if getattr(db_feature, 'size', 0) != 128:
                                print(f"Invalid DB feature size for {sid}: {getattr(db_feature, 'size', 'unknown')}")
                                continue
                            
                            db_feat = np.ascontiguousarray(db_feature, dtype=np.float32).reshape(1, 128)
                            live_feat = np.ascontiguousarray(live_feature, dtype=np.float32).reshape(1, 128)
                            
                            score = sface.match(live_feat, db_feat, cv2.FaceRecognizerSF_FR_COSINE)
                            if score > best_score:
                                best_score = score
                                best_match = sid
                        except Exception as loop_e:
                            print(f"Match error for {sid}: {loop_e}")
                    
                    # threshold for SFace cosine similarity is ~0.363 for true positive exactly
                    # We use 0.36 to be safe but strict
                    confidence_threshold = 0.36
                    
                    # For GUI display, map it to a percentage
                    conf_display = int(max(0, min(100, best_score * 100)))

                    if best_score >= confidence_threshold and best_match != "Unknown":
                        sid = best_match
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
                    else:
                        # Confidence too low
                        name = "Unknown"
                        box_color = (0, 0, 255)
                        bg_color = (0, 0, 200)

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
    for widget in content_area.winfo_children():
        widget.destroy()
        
    # Ensure the model is loaded every time the tab is opened
    reload_classifier()
    
    ctk.CTkLabel(content_area, text="Face Recognition", font=("Segoe UI",28,"bold"), text_color="#3b9dd8").pack(anchor="w", padx=30, pady=(30,10))
    
    # Camera selector
    cam_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    cam_bar.pack(fill="x", padx=30, pady=(0,8))
    ctk.CTkLabel(cam_bar, text="📷 Camera:", font=("Arial",12,"bold"), text_color="gray").pack(side="left", padx=(15,8), pady=8)
    
    cam_btn_refs = {}
    def select_camera(idx):
        if idx == shared.current_camera_index:
            return
            
        shared.switch_camera_live(idx)
        # Instant update for UI feedback
        for i, b in cam_btn_refs.items():
            b.configure(fg_color="#3b9dd8" if i == idx else "#333333")
    
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
    Scans both train_images/ and train_images_admin/ for all .npy files, 
    trains a combined SFace embedding model, and updates the label map.
    """
    try:
        data_dirs = [
            os.path.join(parent_dir, "train_images"),
            os.path.join(parent_dir, "train_images_admin")
        ]
        
        all_files = []
        for d in data_dirs:
            if os.path.isdir(d):
                all_files.extend([(d, f) for f in os.listdir(d) if f.endswith(".npy")])

        if not all_files:
            error_callback("No dataset files (.npy) found in Students or Admin folders.")
            return

        import pickle
        new_db = {}
        total_subjects = len(all_files)
        total_images_processed = 0
        
        sface_bg = cv2.FaceRecognizerSF.create(os.path.join(parent_dir, "dnn_model", "face_recognition_sface.onnx"), "")

        for idx, (dir_path, filename) in enumerate(all_files):
            subject_id = filename[:-4]
            status_callback(f"Extracting 128D Embeddings {idx+1}/{total_subjects}: {subject_id}")
            file_path = os.path.join(dir_path, filename)
            
            try:
                data = np.load(file_path)
                num_imgs = len(data)
                embs = []
                for i, row in enumerate(data):
                    try:
                        img_np = row.reshape((112, 112, 3)).astype("uint8")
                        feature = sface_bg.feature(img_np)
                        embs.append(feature[0])
                        total_images_processed += 1
                    except:
                        continue
                    if i % 10 == 0 or i == num_imgs - 1:
                        current_p = (idx / total_subjects) + ((i + 1) / (num_imgs * total_subjects))
                        progress_callback(current_p, f"Processed {total_images_processed} features...")
                
                if embs:
                    master_emb = np.mean(embs, axis=0)
                    new_db[subject_id] = master_emb
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue

        if not new_db:
            error_callback("No valid embeddings extracted.")
            return

        status_callback("Saving Embedding Database...")
        os.makedirs(os.path.dirname(CLASSIFIER_PATH), exist_ok=True)
        with open(CLASSIFIER_PATH, "wb") as f:
            pickle.dump(new_db, f)
            
        reload_classifier()
        done_callback(total_students, total_images_processed)
    except Exception as e:
        error_callback(str(e))