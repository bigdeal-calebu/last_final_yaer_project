import cv2
from PIL import Image
import os
import sys
from datetime import datetime
import json
import numpy as np
import time

# PATH FIX for MODULAR DB
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from db import get_connection, get_student_by_regno, record_attendance
except:
    get_connection = lambda: None
    get_student_by_regno = lambda x: None
    record_attendance = lambda **k: None

# GLOBAL CAMERA VARIABLES
camera_cap = None
face_cascade = cv2.CascadeClassifier(os.path.join(parent_dir, "cascade/haarcascade_frontalface_default.xml"))
recognizer = cv2.face.LBPHFaceRecognizer_create()
model_loaded = False

# Try to load model
try:
    if os.path.exists("classifier.xml"):
        recognizer.read("classifier.xml")
        model_loaded = True
except:
    model_loaded = False

# Label Map
LABEL_MAP_PATH = os.path.join("models", "label_map.json")
label_map = {}

def load_label_map():
    global label_map
    try:
        if os.path.exists(LABEL_MAP_PATH):
            with open(LABEL_MAP_PATH, "r") as f:
                label_map = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load label_map.json: {e}")
        label_map = {}
load_label_map()

# Camera & detection globals
frame_count = 0
process_every_n_frames = 1
last_faces = []
detection_scale = 0.75
current_camera_index = 0

present_student_ids = set()
present_details_list = []
sidebar_stats_callback = None

unknown_capture_active = False
unknown_frames_to_capture = 0
current_unknown_folder = ""
last_unknown_trigger_time = 0

def start_camera_stream(index=None):
    global camera_cap, current_camera_index
    if index is None:
        index = current_camera_index
    if camera_cap is not None and camera_cap.isOpened():
        return True
    
    # Use default backend to avoid DSHOW Index warning on Windows
    camera_cap = cv2.VideoCapture(index)
    if not camera_cap.isOpened():
        alt = 1 if index == 0 else 0
        camera_cap = cv2.VideoCapture(alt)
        if camera_cap.isOpened():
            current_camera_index = alt
            
    if camera_cap.isOpened():
        camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera_cap.isOpened()

def release_camera_stream():
    global camera_cap
    if camera_cap:
        camera_cap.release()
    camera_cap = None

def switch_camera_live(index):
    global current_camera_index
    current_camera_index = index
    release_camera_stream()

def draw_label(img, text, org, font, scale, txt_color, bg_color, thickness=1):
    (tw, th), bl = cv2.getTextSize(text, font, scale, thickness)
    px, py = max(1, int(6*scale)), max(1, int(4*scale))
    x0, y0 = org[0]-px, org[1]-th-py
    x1, y1 = org[0]+tw+px, org[1]+bl+py
    fh, fw = img.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(fw, x1), min(fh, y1)
    cv2.rectangle(img, (x0, y0), (x1, y1), bg_color, -1)
    cv2.putText(img, text, org, font, scale, txt_color, thickness, cv2.LINE_AA)

FONT = cv2.FONT_HERSHEY_SIMPLEX

def get_camera_frame():
    global camera_cap, frame_count, last_faces, model_loaded
    global unknown_capture_active, unknown_frames_to_capture, current_unknown_folder, last_unknown_trigger_time
    global present_student_ids, present_details_list

    if camera_cap is None or not camera_cap.isOpened():
        if not start_camera_stream():
            return None

    success, frame = camera_cap.read()
    if not success:
        return None

    frame_count += 1
    if frame_count % process_every_n_frames == 0:
        small  = cv2.resize(frame, (0, 0), fx=detection_scale, fy=detection_scale)
        gray_s = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        frontal = face_cascade.detectMultiScale(
            gray_s, scaleFactor=1.1, minNeighbors=12, minSize=(100, 100)
        )

        scale_inv = 1.0 / detection_scale
        last_faces = [(int(x*scale_inv), int(y*scale_inv), int(w*scale_inv), int(h*scale_inv)) for (x,y,w,h) in frontal]

    gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if model_loaded and last_faces else None

    for (x, y, w, h) in last_faces:
        name = "Unknown"
        course = ""
        conf_text = ""
        box_color = (0, 60, 255)
        txt_color = (255, 255, 255)
        bg_color = (0, 40, 180)
        box_thickness = max(1, int(w/80))
        font_scale = max(0.3, min(0.65, w/180.0))
        label_offset = max(5, int(h*0.05))

        if model_loaded and gray_full is not None:
            try:
                # Reduced padding
                pad_top = int(h*0.2)
                pad_side = int(w*0.2)
                pad_bottom = int(h*0.2)
                max_h, max_w = frame.shape[:2]
                rx1 = max(0, x - pad_side)
                ry1 = max(0, y - pad_top)
                rx2 = min(max_w, x + w + pad_side)
                ry2 = min(max_h, y + h + pad_bottom)

                roi = gray_full[ry1:ry2, rx1:rx2]
                if roi.size == 0:
                    roi = gray_full[y:y+h, x:x+w]

                roi_r = cv2.resize(roi, (200, 200))
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                roi_r = clahe.apply(roi_r)

                lbl, conf = recognizer.predict(roi_r)
                if conf < 60:  # stricter threshold
                    student_id_str = label_map.get(str(lbl), "")
                    if student_id_str:
                        name = student_id_str
                        course = "N/A"
                        rec = get_student_by_regno(student_id_str)
                        if rec:
                            name = rec.get("name", student_id_str)
                            course = rec.get("course", "N/A") or "N/A"
                        match_pct = int(100-conf)
                        conf_text = f"{match_pct}%"
                        if match_pct >= 70:
                            box_color, bg_color = (0,140,0),(0,80,0)
                        elif match_pct >= 50:
                            box_color, bg_color = (0,170,40),(0,90,20)
                        else:
                            box_color, bg_color = (0,150,60),(0,80,30)
                        # Record attendance once
                        if student_id_str not in present_student_ids:
                            present_student_ids.add(student_id_str)
                            now = datetime.now()
                            present_details_list.append({
                                'name': name, 'reg': student_id_str, 'course': course,
                                'program': rec.get('program','N/A') if rec else 'N/A',
                                'date': now.strftime("%Y-%m-%d"), 'time': now.strftime("%H:%M:%S")
                            })
                            record_attendance(
                                reg_no=student_id_str, name=name, course=course,
                                program=rec.get('program','N/A') if rec else 'N/A',
                                department=rec.get('department','N/A') if rec else 'N/A',
                                status="Present"
                            )
                            if sidebar_stats_callback:
                                sidebar_stats_callback()
                else:
                    name = "Unknown"
                    conf_text = ""

                # Unknown capture
                if name == "Unknown":
                    now_ts = time.time()
                    if not unknown_capture_active and (now_ts - last_unknown_trigger_time) > 10:
                        base_dir = "unknowns"
                        os.makedirs(base_dir, exist_ok=True)
                        i = 1
                        while os.path.exists(os.path.join(base_dir, f"unknown{i}")):
                            i += 1
                        new_folder = os.path.join(base_dir, f"unknown{i}")
                        os.makedirs(new_folder)
                        current_unknown_folder = new_folder
                        unknown_frames_to_capture = 15
                        unknown_capture_active = True
                        last_unknown_trigger_time = now_ts

                    if unknown_capture_active and unknown_frames_to_capture > 0:
                        face_img = frame[y:y+h, x:x+w]
                        if face_img.size > 0:
                            img_name = f"frame_{16-unknown_frames_to_capture}.jpg"
                            cv2.imwrite(os.path.join(current_unknown_folder, img_name), face_img)
                            unknown_frames_to_capture -= 1
                            if unknown_frames_to_capture == 0:
                                unknown_capture_active = False

            except Exception as e:
                print("Recognition error:", e)
                pass

        # Draw rectangle and labels
        cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, box_thickness)
        corner = max(5, int(w*0.15))
        for cx, cy, dx, dy in [(x,y,1,1),(x+w,y,-1,1),(x,y+h,1,-1),(x+w,y+h,-1,-1)]:
            cv2.line(frame, (cx,cy), (cx+dx*corner, cy), box_color, box_thickness)
            cv2.line(frame, (cx,cy), (cx, cy+dy*corner), box_color, box_thickness)
        label_y = y - label_offset if y > (label_offset+20) else y + h + label_offset + 25
        draw_label(frame, name, (x,label_y), FONT, font_scale, txt_color, bg_color, max(1,int(box_thickness/2)))
        if course:
            course_font_scale = font_scale*0.8
            (tw, th), _ = cv2.getTextSize(name, FONT, font_scale, max(1,int(box_thickness/2)))
            course_y = label_y - (th+10) if y > (label_offset+40) else label_y + (th+10)
            draw_label(frame, course, (x, course_y), FONT, course_font_scale, (220,255,220),(0,70,0),1)
        if conf_text and w>40:
            conf_font_scale = font_scale*0.85
            draw_label(frame, conf_text, (x+w - int(w*0.3), y+h + label_offset + 15), FONT, conf_font_scale, txt_color, (50,50,50), 1)

    return frame

def reload_classifier():
    global recognizer, model_loaded
    try:
        if os.path.exists("classifier.xml"):
            recognizer.read("classifier.xml")
            model_loaded = True
            return True
    except:
        pass
    return False

def train_all_students_bg(on_progress=None, on_status=None, on_done=None, on_error=None):
    """Refactored background trainer for processing all student folders at once."""
    base = "train_images"
    if not os.path.isdir(base):
        base = "Train_images"
    try:
        folders = [f for f in os.listdir(base) if os.path.isdir(os.path.join(base, f))]
    except:
        folders = []
    
    if not folders:
        if on_error: on_error("No student folders found.")
        return

    all_faces, all_ids, new_map = [], [], {}
    total_imgs = 0
    
    for fi, sid in enumerate(folders):
        folder_path = os.path.join(base, sid)
        img_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not img_files: continue
        
        lbl = abs(hash(sid)) % 100000
        new_map[str(lbl)] = sid
        
        for ip in img_files:
            try:
                arr = np.array(Image.open(ip).convert("L"), "uint8")
                all_faces.append(arr)
                all_ids.append(lbl)
                total_imgs += 1
            except: pass
            
        if on_progress: on_progress((fi + 1) / len(folders), f"Loaded {sid} ({fi+1}/{len(folders)})")

    if not all_faces:
        if on_error: on_error("No valid images found.")
        return

    if on_status: on_status("Training...")
    
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(all_faces, np.array(all_ids))
    
    os.makedirs("models", exist_ok=True)
    clf.save("classifier.xml")
    
    try:
        with open(LABEL_MAP_PATH, "w") as f:
            json.dump(new_map, f, indent=2)
    except: pass
    
    reload_classifier()
    load_label_map()
    
    if on_done: on_done(len(folders), total_imgs)
