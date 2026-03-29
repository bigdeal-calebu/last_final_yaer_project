import customtkinter as ctk
import cv2
from PIL import Image
import threading
import os
import sys
import numpy as np

# PATH FIX for project structure
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from admin_dashboard_files import shared
from admin_dashboard_files.shared import start_camera_stream

# AI Models Configuration
AGE_PROTO = os.path.join(parent_dir, "models", "age_deploy.prototxt")
AGE_MODEL = os.path.join(parent_dir, "models", "age_net.caffemodel")
YUNET_PATH = os.path.join(parent_dir, "dnn_model", "face_detection_yunet.onnx")

AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

# Globals for the scanner
age_net = None
yunet = None
scanner_active = False
current_cam_idx = shared.current_camera_index

# Shared data for dual-thread communication
class ScannerState:
    def __init__(self):
        self.frame = None     # Current CV2 frame
        self.pil_img = None   # Current PIL Image for UI
        self.faces = None     # Detected face coordinates
        self.ages = {}        # {face_idx: stable_age_string}
        self.ages_history = {} # {face_idx: [list_of_last_15_results]}
        self.lock = threading.Lock()

state = ScannerState()

def load_ai_models():
    global age_net, yunet
    try:
        if os.path.exists(AGE_PROTO) and os.path.exists(AGE_MODEL):
            age_net = cv2.dnn.readNet(AGE_MODEL, AGE_PROTO)
        
        if os.path.exists(YUNET_PATH):
            yunet = cv2.FaceDetectorYN.create(YUNET_PATH, "", (320, 320))
        return True
    except Exception as e:
        print(f"[Age Prediction] Error loading models: {e}")
        return False

def predict_age(face_frame):
    if age_net is None: return "N/A"
    try:
        blob = cv2.dnn.blobFromImage(face_frame, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
        age_net.setInput(blob)
        predictions = age_net.forward()
        age = AGE_LIST[predictions[0].argmax()]
        return age
    except:
        return "?"

def show_prediction_content(content_area, responsive_manager):
    global scanner_active
    scanner_active = False # Reset flag for clean start
    
    # 1. Clear existing widgets
    for widget in content_area.winfo_children():
        widget.destroy()

    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 30

    # 2. Header
    ctk.CTkLabel(content_area, text="🧠 AI Live Age Scanner", 
                 font=("Segoe UI", 22 if is_small else 28, "bold"), 
                 text_color="#3b9dd8").pack(anchor="w", padx=side_pad, pady=(20, 5))
    
    if not is_small:
        ctk.CTkLabel(content_area, text="Using deep learning to estimate age from facial features in real-time.",
                     font=("Arial", 12), text_color="gray").pack(anchor="w", padx=side_pad, pady=(0, 15))

    # 3. Scanner Container
    main_frame = ctk.CTkFrame(content_area, fg_color="#101010", corner_radius=15)
    main_frame.pack(fill="both", expand=True, padx=side_pad, pady=(0, 10))

    # 4. Results Panel (Responsive packing)
    # If small, put results at bottom as a horizontal strip. If desktop, put on right.
    info_panel_side = "bottom" if is_small else "right"
    info_panel_fill = "x" if is_small else "y"
    info_panel_width = 250 if not is_small else 200 # Fixed: Cannot be None
    
    info_panel = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", width=info_panel_width)
    info_panel.pack(side=info_panel_side, fill=info_panel_fill, padx=10, pady=10)

    # Internal Layout for Info Panel
    if is_small:
        # Compact Horizontal Grid for Mobile
        info_inner = ctk.CTkFrame(info_panel, fg_color="transparent")
        info_inner.pack(fill="x", padx=10, pady=5)
        info_inner.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Status
        s_box = ctk.CTkFrame(info_inner, fg_color="transparent")
        s_box.grid(row=0, column=0)
        ctk.CTkLabel(s_box, text="STATUS", font=("Arial", 10, "bold"), text_color="gray").pack()
        status_lbl = ctk.CTkLabel(s_box, text="IDLE", font=("Arial", 12, "bold"), text_color="#e74c3c")
        status_lbl.pack()
        
        # Model
        m_box = ctk.CTkFrame(info_inner, fg_color="transparent")
        m_box.grid(row=0, column=1)
        ctk.CTkLabel(m_box, text="MODEL", font=("Arial", 10, "bold"), text_color="gray").pack()
        model_lbl = ctk.CTkLabel(m_box, text="...", font=("Arial", 11, "bold"), text_color="white")
        model_lbl.pack()
        
        # Camera Source
        c_box = ctk.CTkFrame(info_inner, fg_color="transparent")
        c_box.grid(row=0, column=2)
        def on_cam_mobile(c):
             global current_cam_idx, scanner_active
             idx = 0 if "0" in c else 1
             current_cam_idx = idx
             if scanner_active:
                 scanner_active = False
                 content_area.after(800, start_scanner)
        
        cam_selector = ctk.CTkOptionMenu(c_box, values=["Cam 0", "Cam 1"], 
                                         width=80, height=25, font=("Arial", 10), command=on_cam_mobile)
        cam_selector.set(f"Cam {current_cam_idx}")
        cam_selector.pack(pady=2)

        # Detection Result
        d_box = ctk.CTkFrame(info_inner, fg_color="transparent")
        d_box.grid(row=0, column=3)
        ctk.CTkLabel(d_box, text="AGE", font=("Arial", 10, "bold"), text_color="gray").pack()
        age_lbl_result = ctk.CTkLabel(d_box, text="...", font=("Arial", 16, "bold"), text_color="#00c853")
        age_lbl_result.pack()

    else:
        # Professional Vertical Stack for Desktop
        ctk.CTkLabel(info_panel, text="STATUS", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(15, 5))
        status_lbl = ctk.CTkLabel(info_panel, text="IDLE", font=("Arial", 16, "bold"), text_color="#e74c3c")
        status_lbl.pack()

        ctk.CTkLabel(info_panel, text="MODEL", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(20, 5))
        model_lbl = ctk.CTkLabel(info_panel, text="LOADING...", font=("Arial", 13, "bold"), text_color="white")
        model_lbl.pack()

        ctk.CTkLabel(info_panel, text="CAMERA SOURCE", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(25, 5))
        def on_cam_desktop(choice):
            global current_cam_idx, scanner_active
            idx = 0 if "0" in choice else 1
            current_cam_idx = idx
            if scanner_active:
                scanner_active = False
                content_area.after(800, start_scanner)

        cam_selector = ctk.CTkOptionMenu(info_panel, values=["Camera 0", "Camera 1"], 
                                         height=30, command=on_cam_desktop)
        cam_selector.set(f"Camera {current_cam_idx}")
        cam_selector.pack(pady=5)

        ctk.CTkLabel(info_panel, text="DETECTION", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(35, 5))
        age_lbl_result = ctk.CTkLabel(info_panel, text="...", font=("Arial", 32, "bold"), text_color="#00c853")
        age_lbl_result.pack()

    # 5. Main Camera Area
    cam_display = ctk.CTkLabel(main_frame, text="", fg_color="#000000", corner_radius=10)
    cam_display.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    # 6. UI Logic
    def update_model_status():
        if load_ai_models():
            model_lbl.configure(text="🧠 READY", text_color="#00c853")
        else:
            model_lbl.configure(text="❌ ERROR", text_color="#e74c3c")
    
    content_area.after(100, update_model_status)

    def update_ui_main():
        if not scanner_active: return
        
        try:
            with state.lock:
                current_pil = state.pil_img
                current_ages_dict = state.ages.copy()
            
            if current_pil is not None:
                # Force Portrait Aspect: Height should be greater than width
                dh = cam_display.winfo_height()
                if dh < 100: dh = 500
                dw = int(dh * 0.75) # Maintain 3:4 Portrait Ratio
                
                ctk_img = ctk.CTkImage(current_pil, size=(dw, dh))
                cam_display.configure(image=ctk_img)
            
            if current_ages_dict:
                first_age = list(current_ages_dict.values())[0]
                age_lbl_result.configure(text=first_age)
        except: pass

        if scanner_active:
            content_area.after(30, update_ui_main)

    def start_scanner():
        global scanner_active
        if scanner_active: return
        
        from admin_dashboard_files.shared import release_camera_stream
        release_camera_stream()
        
        scanner_active = True
        status_lbl.configure(text="SCANNING", text_color="#27ae60")
        
        threading.Thread(target=camera_reader_loop, args=(current_cam_idx,), daemon=True).start()
        threading.Thread(target=ai_worker_loop, daemon=True).start()
        update_ui_main()

    def camera_reader_loop(cam_idx):
        global scanner_active
        cap = cv2.VideoCapture(cam_idx)
        if not cap.isOpened(): cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            scanner_active = False # Signal UI will stop
            return

        print("[Age Scanner] Reader loop (portrait) active.")
        while scanner_active:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            
            # 📱 PORTRAIT CROP: Crop sides to make it 3:4 (Portrait)
            target_w = int(h * 0.75) 
            if w > target_w:
                start_x = (w - target_w) // 2
                frame = frame[:, start_x : start_x + target_w]
            
            # Draw Overlays using SHARED analysis
            with state.lock:
                current_faces = state.faces
                current_ages = state.ages.copy()

            if current_faces is not None:
                for idx, face in enumerate(current_faces):
                    x, y, fw, fh = face[:4].astype(int)
                    cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 200, 83), 2)
                    label = current_ages.get(idx, "Computing...")
                    cv2.putText(frame, f"Age: {label}", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 83), 2)

            # Convert to PIL and pass to main thread (DO NOT UPDATE UI HERE)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            
            with state.lock:
                state.frame = frame.copy() # For AI thread
                state.pil_img = pil_img     # For UI thread
            
        cap.release()

    def ai_worker_loop():
        global scanner_active
        from collections import Counter
        print("[Age Scanner] AI Brain loop active.")
        count = 0
        while scanner_active:
            f = None
            with state.lock: f = state.frame.copy() if state.frame is not None else None
            
            if f is not None:
                h, w = f.shape[:2]
                if yunet:
                    yunet.setInputSize((w, h))
                    _, det = yunet.detect(f)
                    with state.lock: state.faces = det
                    
                    if det is not None:
                        for idx, face in enumerate(det):
                            # Predicted every few ticks for responsiveness
                            if count % 3 == 0:
                                x, y, fw, fh = face[:4].astype(int)
                                
                                # 🆕 NEW: Add 30% CONTEXT PADDING for better accuracy (25+ bracket)
                                # This helps the AI see forehead, hair, and jawline structure.
                                pad_w = int(fw * 0.3)
                                pad_h = int(fh * 0.3)
                                px = max(0, x - pad_w)
                                py = max(0, y - pad_h)
                                pw = min(w - px, fw + 2 * pad_w)
                                ph = min(h - py, fh + 2 * pad_h)
                                
                                crop = f[py:py+ph, px:px+pw]
                                if crop.size > 0:
                                    age_str = predict_age(crop)
                                    
                                    # Majority Voting Smoothing logic (Higher frame count for 25+ stability)
                                    with state.lock:
                                        hist = state.ages_history.get(idx, [])
                                        hist.append(age_str)
                                        if len(hist) > 20: hist.pop(0) # Store last 20 scans
                                        state.ages_history[idx] = hist
                                        
                                        # Only show the most frequent result (The "Mode")
                                        stable_age = Counter(hist).most_common(1)[0][0]
                                        state.ages[idx] = stable_age
                count += 1
            import time
            time.sleep(0.01)

    # placeholder
    try:
        placeholder = ctk.CTkImage(Image.new('RGB', (640, 480), (10, 10, 10)), size=(480, 200 if is_small else 320))
        cam_display.configure(image=placeholder)
    except: pass

    # Control Button
    btn_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    btn_frame.pack(fill="x", padx=side_pad, pady=(0, 20))
    
    ctk.CTkButton(btn_frame, text="🚀 START AI SCANNER", height=45, font=("Arial", 14, "bold"),
                  fg_color="#3b9dd8", hover_color="#2980b9", command=start_scanner).pack(pady=10)
