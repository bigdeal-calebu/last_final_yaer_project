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

# Face Tracking & Stability Memory
FACE_TRACKER = {}        # {id: (box, frames_missing)}
RECOGNITION_HISTORY = {} # {id: [list_of_last_10_names]}
BLINK_STATES = {}        # {id: True/False} (Mandatory Verification)
EYE_HISTORY = {}         # {id: [last_10_brightness_values for left, last_10_for_right]}
NOSE_HISTORY = {}        # {id: [last_5_nose_positions]}
NEXT_FACE_ID = 0

def get_face_id(box):
    global NEXT_FACE_ID
    x, y, w, h = box
    cx, cy = x + w//2, y + h//2
    # Try to find a previous face near this centroid
    for fid in list(FACE_TRACKER.keys()):
        prev_box, m = FACE_TRACKER[fid]
        px, py, pw, ph = prev_box
        pcx, pcy = px + pw//2, py + ph//2
        # If within 60 pixels, it's the same person
        if abs(cx - pcx) < 60 and abs(cy - pcy) < 60:
            FACE_TRACKER[fid] = (box, 0)
            return fid
    # New face
    fid = NEXT_FACE_ID
    NEXT_FACE_ID += 1
    FACE_TRACKER[fid] = (box, 0)
    return fid

# OpenCV YuNet Face Detector
# ... existing yunet code ...
try:
    yunet_path = os.path.join(parent_dir, "dnn_model", "face_detection_yunet.onnx")
    yunet = cv2.FaceDetectorYN.create(yunet_path, "", (320, 320))
except Exception as e:
    print(f"Error loading YuNet model: {e}")
    yunet = None

# OpenCV SFace (Deep Learning Embeddings)
try:
    sface_path = os.path.join(parent_dir, "dnn_model", "face_recognition_sface.onnx")
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
    
    # 📱 PORTRAIT CROP: Crop sides to make it 3:4 (Portrait)
    target_w = int(h_img * 0.75) 
    if w_img > target_w:
        start_x = (w_img - target_w) // 2
        frame = frame[:, start_x : start_x + target_w]
        w_img = target_w

    faces = []
    
    if yunet is not None:
        yunet.setInputSize((w_img, h_img))
        _, yunet_faces = yunet.detect(frame)
        if yunet_faces is not None:
            for face_data in yunet_faces:
                box = face_data[0:4].astype("int")
                (startX, startY, w, h) = box
                startX, startY = max(0, startX), max(0, startY)
                endX, endY = min(w_img - 1, startX + w), min(h_img - 1, startY + h)
                w, h = endX - startX, endY - startY
                if w > 40 and h > 40:
                    faces.append((startX, startY, w, h, face_data))

    detections = []
    
    # Update tracker: Cleanup stale data
    for fid in list(FACE_TRACKER.keys()):
        box, m = FACE_TRACKER[fid]
        FACE_TRACKER[fid] = (box, m + 1)
        if m > 30:
            FACE_TRACKER.pop(fid, None)
            RECOGNITION_HISTORY.pop(fid, None)
            BLINK_STATES.pop(fid, None)
            EYE_HISTORY.pop(fid, None)
            NOSE_HISTORY.pop(fid, None)

    for (x, y, w, h, face_data_arr) in faces:
        fid = get_face_id((x, y, w, h))
        current_match = "Unknown"
        current_conf = 0.0
        
        # 🧪 ZERO-MOTION ACTIVE BLINK Logic
        blinked = BLINK_STATES.get(fid, False)
        if not blinked:
            # Anchor point (Nose) to detect head motion
            nx, ny = int(face_data_arr[8]), int(face_data_arr[9])
            n_hist = NOSE_HISTORY.get(fid, [])
            n_hist.append((nx, ny))
            if len(n_hist) > 5: n_hist.pop(0)
            NOSE_HISTORY[fid] = n_hist
            
            # Head Motion Lock: If the nose moved more than 3 pixels, it's too much motion
            head_still = True
            if len(n_hist) > 2:
                dx = abs(n_hist[-1][0] - n_hist[-2][0])
                dy = abs(n_hist[-1][1] - n_hist[-2][1])
                if dx > 3 or dy > 3: head_still = False

            # Monitor eyes (YuNet points 4-7 are left/right eyes)
            lx, ly = int(face_data_arr[4]), int(face_data_arr[5])
            rx, ry = int(face_data_arr[6]), int(face_data_arr[7])
            
            if head_still and lx > 0 and rx > 0:
                # Track both eyes for Synchronized Liveness
                eyel_strip = frame[max(0,ly-4):ly+4, max(0,lx-4):lx+4]
                eyer_strip = frame[max(0,ry-4):ry+4, max(0,rx-4):rx+4]
                
                if eyel_strip.size > 0 and eyer_strip.size > 0:
                    ml = np.mean(cv2.cvtColor(eyel_strip, cv2.COLOR_BGR2GRAY))
                    mr = np.mean(cv2.cvtColor(eyer_strip, cv2.COLOR_BGR2GRAY))
                    
                    e_hist = EYE_HISTORY.get(fid, [[], []])
                    e_hist[0].append(ml); e_hist[1].append(mr)
                    if len(e_hist[0]) > 10: e_hist[0].pop(0); e_hist[1].pop(0)
                    EYE_HISTORY[fid] = e_hist
                    
                    # Detection: Both eyes must show a dip simultaneously
                    if len(e_hist[0]) > 5:
                        al, ar = np.mean(e_hist[0][:-1]), np.mean(e_hist[1][:-1])
                        # Dip threshold (15% drop)
                        if e_hist[0][-1] < (al * 0.85) and e_hist[1][-1] < (ar * 0.85):
                            BLINK_STATES[fid] = True
                            blinked = True

        if model_loaded and sface is not None:
            try:
                aligned_crop = sface.alignCrop(frame, face_data_arr)
                if aligned_crop is not None:
                    # 🛡️ BIONIC Liveness Filters
                    gray_crop = cv2.cvtColor(aligned_crop, cv2.COLOR_BGR2GRAY)
                    liveness_var = cv2.Laplacian(gray_crop, cv2.CV_64F).var()
                    hsv_crop = cv2.cvtColor(aligned_crop, cv2.COLOR_BGR2HSV)
                    avg_sat = np.mean(hsv_crop[:,:,1])
                    
                    is_live = (liveness_var > 125) and (15 < avg_sat < 165)
                    
                    if not is_live:
                        current_match = "SPOOF"
                        # Reset blink history on spoof detect to be safe
                        BLINK_STATES[fid] = False
                    elif not blinked:
                        current_match = "WAIT_FOR_BLINK"
                    else:
                        live_feature = sface.feature(aligned_crop)
                        best_match, best_score = "Unknown", -1.0
                        for sid, db_feature in embeddings_db.items():
                            try:
                                db_feat = np.ascontiguousarray(db_feature, dtype=np.float32).reshape(1, 128)
                                live_feat = np.ascontiguousarray(live_feature, dtype=np.float32).reshape(1, 128)
                                score = sface.match(live_feat, db_feat, cv2.FaceRecognizerSF_FR_COSINE)
                                if score > best_score:
                                    best_score, best_match = score, sid
                            except: continue
                        
                        if best_score >= 0.78:
                            current_match = best_match
                            current_conf = int(min(99, 90 + (best_score - 0.78) * 40)) 
                        else:
                            current_match = "Unknown"
                            current_conf = int(best_score * 100)
            except: pass

        # 🧠 Stability Memory
        hist = RECOGNITION_HISTORY.get(fid, [])
        hist.append(current_match)
        if len(hist) > 15: hist.pop(0)
        RECOGNITION_HISTORY[fid] = hist
        
        from collections import Counter
        stable_sid = Counter(hist).most_common(1)[0][0]
        
        # Display logic
        name, reg_no, course, session = "Scanning Candidate...", "", "", ""
        box_color, bg_color = (0, 0, 255), (0, 0, 200)
        font_scale = max(0.45, min(0.7, w/150.0))

        if stable_sid == "SPOOF":
            name = "⚠️ SPOOF DETECTED!"
            course = "PLEASE USE LIVE FACE"
            box_color, bg_color = (0, 0, 255), (0, 0, 255)
        elif stable_sid == "WAIT_FOR_BLINK":
            name = "⚠️ Liveness Verification"
            course = "PLEASE BLINK YOUR EYES"
            box_color = (255, 100, 0) # Cyan/Orange prompt for attention
            bg_color = (0, 0, 0)
        elif stable_sid == "Unknown":
            # Only show Unknown after we have at least 5 samples to avoid flickering
            if len(hist) >= 5:
                name = "Unknown"
                box_color, bg_color = (0, 0, 255), (0, 0, 180)
            else:
                name = f"Scanning... ({len(hist)}/5)"
                box_color, bg_color = (255, 165, 0), (0, 0, 0)
        else:
            student_info = get_cached_student(stable_sid)
            if student_info:
                display_conf = 99 if current_conf >= 98 else current_conf
                name = f"{student_info['full_name']} ({display_conf}%)"
                course, session = student_info["course"], student_info["session"]
                dept = student_info["department"]
                box_color, bg_color, reg_no = (0, 255, 0), (0, 180, 0), stable_sid

                # Attendance Recording
                now = datetime.now()
                if stable_sid not in shared.present_student_ids:
                    shared.present_student_ids.add(stable_sid)
                    shared.present_details_list.append({
                        'name': name, 'reg': stable_sid, 'course': course,
                        'session': session, 'date': now.strftime("%Y-%m-%d"),
                        'time': now.strftime("%H:%M:%S")
                    })
                    threading.Thread(target=record_attendance, kwargs={
                        'reg_no': stable_sid, 'name': name, 'course': course,
                        'program': session, 'department': dept, 'status': "Present"
                    }, daemon=True).start()
                    if shared.sidebar_stats_callback: shared.sidebar_stats_callback()

                detections.append({"reg_no": stable_sid, "name": name})

        # Visuals
        cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
        # corners
        L, t = int(w * 0.15), 4
        cv2.line(frame, (x, y), (x+L, y), box_color, t)
        cv2.line(frame, (x, y), (x, y+L), box_color, t)
        cv2.line(frame, (x+w, y), (x+w-L, y), box_color, t)
        cv2.line(frame, (x+w, y), (x+w, y+L), box_color, t)
        cv2.line(frame, (x, y+h), (x+L, y+h), box_color, t)
        cv2.line(frame, (x, y+h), (x, y+h-L), box_color, t)
        cv2.line(frame, (x+w, y+h), (x+w-L, y+h), box_color, t)
        cv2.line(frame, (x+w, y+h), (x+w, y+h-L), box_color, t)

        draw_label(frame, name, (x, y - 10), FONT, font_scale, (255, 255, 255), bg_color, thickness=2)
        
        info_bg = (30, 30, 30)
        start_y = y + h + 25
        spacing = max(22, int(25 * (font_scale/0.5)))
        
        if reg_no: 
            draw_label(frame, f"ID: {reg_no}", (x, start_y), FONT, font_scale*0.85, (0, 255, 255), info_bg, thickness=1)
            start_y += spacing
            draw_label(frame, course, (x, start_y), FONT, font_scale*0.85, (255, 200, 0), info_bg, thickness=1)
            start_y += spacing
            draw_label(frame, f"Session: {session}", (x, start_y), FONT, font_scale*0.85, (150, 255, 150), info_bg, thickness=1)

    return frame, detections

# ---------------- GUI ----------------
def show_face_recognition_content(content_area, responsive_manager):
    for widget in content_area.winfo_children():
        widget.destroy()
        
    # Ensure the model is loaded every time the tab is opened
    reload_classifier()
    
    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 30
    
    ctk.CTkLabel(content_area, text="Face Recognition", font=("Segoe UI", 24 if is_small else 28, "bold"), text_color="#3b9dd8").pack(anchor="w", padx=side_pad, pady=(30,10))
    
    # Camera selector
    cam_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    cam_bar.pack(fill="x", padx=side_pad, pady=(0,8))
    
    label_side = "top" if is_small else "left"
    ctk.CTkLabel(cam_bar, text="📷 Camera:", font=("Arial",12,"bold"), text_color="gray").pack(side=label_side, padx=(15,8), pady=(8,2) if is_small else 8)
    
    btn_frame = ctk.CTkFrame(cam_bar, fg_color="transparent")
    btn_frame.pack(side=label_side, padx=5, pady=(2,8) if is_small else 0)

    
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
        
        btn_w, btn_h = (100, 32) if not is_small else (80, 28)
        b = ctk.CTkButton(btn_frame, text=btn_text, width=btn_w, height=btn_h,
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
    view_w, view_h = (640, 480) if not is_small else (320, 240)
    camera_card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    camera_card.pack(fill="both" if not is_small else "x", expand=True, padx=side_pad, pady=(0,20))
    viewport = ctk.CTkLabel(camera_card, text="", fg_color="black", height=view_h, corner_radius=10)
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
                
                # 📐 Dynamic Portrait Viewport: Always maintain 3:4 Vertical Aspect
                vh = viewport.winfo_height()
                if vh < 100: vh = 480 if not responsive_manager.is_small() else 240
                vw = int(vh * 0.75)
                
                img = Image.fromarray(cv2.resize(frame_rgb, (vw, vh)))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(vw, vh))
                
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
        done_callback(len(new_db), total_images_processed)
    except Exception as e:
        error_callback(str(e))