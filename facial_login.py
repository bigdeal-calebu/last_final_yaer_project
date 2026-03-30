import cv2
import customtkinter as ctk
import threading
import os
import numpy as np
import warnings
from PIL import Image
from admin_dashboard_files import shared
import db

# ── AI MODELS ──────────────────────────────────────────
parent_dir = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_PATH = os.path.join(parent_dir, "models", "embeddings.pkl")

# YuNet Detector & SFace Recognizer
yunet_path = os.path.join(parent_dir, "dnn_model", "face_detection_yunet.onnx")
sface_path = os.path.join(parent_dir, "dnn_model", "face_recognition_sface.onnx")

try:
    yunet = cv2.FaceDetectorYN.create(yunet_path, "", (320, 320))
    sface = cv2.FaceRecognizerSF.create(sface_path, "")
except Exception as e:
    print(f"Error loading AI models: {e}")
    yunet = None
    sface = None

# Global Embeddings Database
embeddings_db = {}
model_loaded = False

def reload_classifier():
    global embeddings_db, model_loaded
    import pickle
    try:
        if os.path.exists(CLASSIFIER_PATH):
            with open(CLASSIFIER_PATH, "rb") as f:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=DeprecationWarning)
                    embeddings_db = pickle.load(f)
            model_loaded = len(embeddings_db) > 0
            return True
    except: pass
    return False

reload_classifier()

# ── LOGIC ──────────────────────────────────────────────
def show_facial_login_ui(parent_frame, on_user_success, on_admin_success, on_back_to_manual):
    """
    Shows a camera UI for facial login. Once recognized, triggers success callbacks.
    """
    for widget in parent_frame.winfo_children():
        widget.destroy()

    reload_classifier()

    # Container - Reduced padding for tiny screens
    card = ctk.CTkFrame(parent_frame, fg_color="#1a1c1e", corner_radius=30, border_width=2, border_color="#333")
    card.pack(expand=True, padx=(5 if parent_frame.winfo_width() < 400 else 20), 
              pady=(5 if parent_frame.winfo_width() < 400 else 20), fill="both")
    
    # Top Bar (Back button and title)
    top_bar = ctk.CTkFrame(card, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=10)

    # Back button
    back_btn = ctk.CTkButton(top_bar, text="← Back", width=80, height=30, command=on_back_to_manual, 
                             fg_color="#333", text_color="orange", font=("Arial", 11, "bold"))
    back_btn.pack(side="left")

    # Title
    title_label = ctk.CTkLabel(card, text="FACIAL SCAN LOGIN", font=("Arial", 28, "bold"), text_color="#2ECC71")
    title_label.pack(pady=(10, 5))
    
    subtitle_label = ctk.CTkLabel(card, text="Look directly at the camera to sign in", font=("Arial", 13), text_color="gray")
    subtitle_label.pack(pady=(0, 15))

    # Camera selector bar - Refactored for easy re-packing
    cam_bar = ctk.CTkFrame(card, fg_color="#1a1c1e", corner_radius=10)
    cam_bar.pack(fill="x", padx=40, pady=(0, 10))
    
    cam_label = ctk.CTkLabel(cam_bar, text="📷 Select Camera:", font=("Arial", 12, "bold"), text_color="gray")
    cam_label.pack(side="left", padx=(15, 8))
    
    # Inner sub-frame for button row to allow wrapping/stacking
    cam_btn_frame = ctk.CTkFrame(cam_bar, fg_color="transparent")
    cam_btn_frame.pack(side="left", fill="x")

    cam_btn_refs = {}
    def select_camera(idx):
        if idx == shared.current_camera_index: return
        shared.switch_camera_live(idx)
        for i, b in cam_btn_refs.items():
            b.configure(fg_color="#3b9dd8" if i == idx else "#333")

    # Loop through all detected cameras
    for cam_idx in shared.available_camera_indices:
        btn_text = "Primary" if cam_idx == 0 else f"Camera {cam_idx}"
        if cam_idx == 1: btn_text = "Secondary"
        
        b = ctk.CTkButton(cam_btn_frame, text=btn_text, width=90, height=28, 
                          fg_color="#3b9dd8" if cam_idx == shared.current_camera_index else "#333",
                          font=("Arial", 11, "bold"), command=lambda i=cam_idx: select_camera(i))
        b.pack(side="left", padx=4)
        cam_btn_refs[cam_idx] = b

    # Camera Preview
    preview_container = ctk.CTkFrame(card, fg_color="black", corner_radius=20, border_width=2, border_color="#444")
    preview_container.pack(fill="both", expand=True, padx=40, pady=(0, 20))
    
    viewport = ctk.CTkLabel(preview_container, text="", fg_color="black", height=400)
    viewport.pack(fill="both", expand=True, padx=5, pady=5)

    status_lbl = ctk.CTkLabel(card, text="Detecting Face...", font=("Arial", 15, "bold"), text_color="#F39C12")
    status_lbl.pack(pady=5)

    # Recognition Threading
    loop_active = [True]
    def on_close(): 
        loop_active[0] = False
    
    # Wrap back button to stop loop
    def safe_back():
        on_close()
        on_back_to_manual()

    # Update back button reference (already done in top_bar above, but let's replace the duplicate)
    back_btn.configure(command=safe_back)

    # Hack to allow parent to stop the loop when switching back
    parent_frame.stop_facial_loop = on_close

    def verify_user_and_login(sid):
        """Checks if sid is a registered student and triggers login."""
        # 1. Check Students
        student = db.get_student_by_regno(sid)
        if student:
            student['name'] = student.get('full_name', sid)
            on_user_success(student)
            return True
        
        status_lbl.configure(text=f"Unauthorized: {sid}", text_color="red")
        viewport.after(2000, lambda: safe_back())
        return False

    camera_timeout_count = [0]
    retry_btn = [None]

    def retry_camera():
        if retry_btn[0]: retry_btn[0].destroy()
        retry_btn[0] = None
        camera_timeout_count[0] = 0
        status_lbl.configure(text="Retrying Camera...", text_color="#F39C12")
        threading.Thread(target=lambda: shared.start_camera_stream(), daemon=True).start()

    def update_frame():
        if not loop_active[0] or not parent_frame.winfo_exists(): return
        
        try:
            if not shared.camera_cap.isOpened():
                camera_timeout_count[0] += 1
                if camera_timeout_count[0] > 50: # ~5 seconds
                    status_lbl.configure(text="CAMERA ERROR: Not Detected", text_color="red")
                    if not retry_btn[0]:
                        retry_btn[0] = ctk.CTkButton(card, text="🔄 RETRY CAMERA", command=retry_camera, fg_color="#E74C3C")
                        retry_btn[0].pack(pady=5)
                else:
                    status_lbl.configure(text="Waiting for Camera...", text_color="#F39C12")
                
                viewport.after(100, update_frame)
                return

            if retry_btn[0]: 
                retry_btn[0].destroy()
                retry_btn[0] = None

            ret, frame = shared.camera_cap.read()
            if not ret: 
                viewport.after(100, update_frame)
                return

            # Recognition Logic
            h, w = frame.shape[:2]
            yunet.setInputSize((w, h))
            _, faces = yunet.detect(frame)
            
            recognized_sid = None
            
            if faces is not None:
                for face_data in faces:
                    box = face_data[0:4].astype("int")
                    x, y, fw, fh = box
                    cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
                    
                    if model_loaded and sface:
                        aligned = sface.alignCrop(frame, face_data)
                        if aligned is not None:
                            live_feat = sface.feature(aligned)
                            best_score = -1.0
                            best_match = None
                            
                            for sid, db_feat in embeddings_db.items():
                                if getattr(db_feat, 'size', 0) != 128: continue
                                score = sface.match(live_feat, db_feat.reshape(1, 128), cv2.FaceRecognizerSF_FR_COSINE)
                                if score > best_score:
                                    best_score = score
                                    best_match = sid
                            
                            if best_score >= 0.78:
                                recognized_sid = best_match
                                cv2.putText(frame, f"Match: {best_match}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            else:
                                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Convert to UI Image
            img = Image.fromarray(cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB))
            ctk_img = ctk.CTkImage(img, size=(640, 480))
            viewport.configure(image=ctk_img)
            viewport.image = ctk_img

            if recognized_sid:
                status_lbl.configure(text=f"Welcome {recognized_sid}! Logging in...", text_color="#2ECC71")
                loop_active[0] = False # Stop loop
                # Small delay for visual feedback
                viewport.after(800, lambda: verify_user_and_login(recognized_sid))
                return

        except Exception as e:
            print(f"Facial Login Error: {e}")
            
        if loop_active[0]:
            viewport.after(33, update_frame)

    # ── RESPONSIVENESS ──────────────────────────────────
    def on_resize(event=None):
        if not card.winfo_exists(): return
        width = parent_frame.winfo_width()
        
        # Tiny (< 400px) layout logic
        if width < 400: 
            vh = max(200, parent_frame.winfo_height() - 320)
            fs = 18
            cpad = 10
            card_pad = 5
            
            # Stack camera bar vertically
            cam_label.pack_configure(side="top", anchor="center", padx=0, pady=(5, 2))
            cam_btn_frame.pack_configure(side="top", fill="x", anchor="center")
            for b in cam_btn_refs.values():
                b.pack_configure(side="left", expand=True) # Spread buttons in the new stack
                
        elif width < 600: # Mobile
            vh = 300
            fs = 22
            cpad = 20
            card_pad = 15
            
            # Reset camera bar to horizontal
            cam_label.pack_configure(side="left", anchor="center", padx=(15, 8), pady=0)
            cam_btn_frame.pack_configure(side="left", fill="x")
            for b in cam_btn_refs.values():
                b.pack_configure(side="left", expand=False)
        else: # Tablet/Desktop
            vh = 400
            fs = 28
            cpad = 40
            card_pad = 20
            
            cam_label.pack_configure(side="left", anchor="center", padx=(15, 8), pady=0)
            cam_btn_frame.pack_configure(side="left", fill="x")
            for b in cam_btn_refs.values():
                b.pack_configure(side="left", expand=False)
            
        viewport.configure(height=vh)
        preview_container.pack_configure(padx=cpad)
        cam_bar.pack_configure(padx=cpad)
        card.pack_configure(padx=card_pad, pady=card_pad)
        title_label.configure(font=("Arial", fs, "bold"))

    parent_frame.bind("<Configure>", on_resize)
    on_resize()

    # Start loop
    threading.Thread(target=lambda: shared.start_camera_stream(), daemon=True).start()
    update_frame()
