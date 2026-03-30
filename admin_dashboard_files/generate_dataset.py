import cv2
import os
import numpy as np
import time
import threading
from PIL import Image, ImageTk
import customtkinter as ctk
import admin_dashboard_files.shared as shared
import zipfile
from tkinter import filedialog
import io

def show_generate_dataset_content(content_area, responsive_manager):
    for widget in content_area.winfo_children():
        widget.destroy()

    # ---------- UI HEADER ----------
    ctk.CTkLabel(
        content_area,
        text="Generate Dataset",
        font=("Segoe UI", 28, "bold"),
        text_color="#2ECC71"
    ).pack(anchor="w", padx=30, pady=(30, 20))

    main_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=30, pady=10)

    is_small = responsive_manager.is_small()

    # ---------------- RIGHT PANEL (TOP on mobile) ----------------
    cam_w, cam_h = (480, 360) if not is_small else (320, 240)
    camera_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15, width=cam_w, height=cam_h)
    camera_frame.pack(side="top" if is_small else "right", padx=15, pady=15)
    camera_frame.pack_propagate(False)

    viewport = ctk.CTkLabel(camera_frame, text="", fg_color="black")
    viewport.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- LEFT PANEL (CONTROLS) ----------------
    ctrl_w = 320 if not is_small else 0
    controls_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15, width=ctrl_w)
    controls_frame.pack(side="top" if is_small else "left", fill="both" if is_small else "y", padx=(0, 20), pady=0)


    ctk.CTkLabel(
        controls_frame,
        text="INPUT METHOD",
        font=("Arial", 14, "bold"),
        text_color="gray"
    ).pack(pady=(20, 5))

    mode_var = ctk.StringVar(value="Camera Capture")
    mode_switch = ctk.CTkSegmentedButton(controls_frame, values=["Camera Capture", "ZIP Upload"], 
                                         variable=mode_var, selected_color="#3498DB", height=40)
    mode_switch.pack(fill="x", padx=20, pady=(0, 20))

    # --- Mode Containers ---
    camera_controls_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    camera_controls_frame.pack(fill="x")
    
    zip_controls_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    # Not packed yet
    
    def switch_mode(*args):
        if mode_var.get() == "Camera Capture":
            zip_controls_frame.pack_forget()
            camera_controls_frame.pack(fill="x")
            camera_frame.pack(side="top" if is_small else "right", padx=15, pady=15)
        else:
            camera_controls_frame.pack_forget()
            camera_frame.pack_forget()
            zip_controls_frame.pack(fill="x", pady=20)
            
    mode_var.trace_add("write", switch_mode)

    ctk.CTkLabel(
        camera_controls_frame,
        text="CAMERA CONFIGURATION",
        font=("Arial", 14, "bold"),
        text_color="gray"
    ).pack(pady=(10, 10))

    # ---------------- Camera Selection (Inside camera_controls_frame) ----------------
    ctk.CTkLabel(camera_controls_frame, text="Camera Source:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 3))
    cam_row_ds = ctk.CTkFrame(camera_controls_frame, fg_color="transparent")
    cam_row_ds.pack(fill="x", padx=20, pady=(0, 12))
    ds_cam_btns = {}

    def select_cam_ds(idx):
        if idx == shared.current_camera_index:
            return
        shared.switch_camera_live(idx)
        for i, b in ds_cam_btns.items():
            b.configure(fg_color="#2ECC71" if i == idx else "#333333")

    for ci in [0, 1]:
        is_avail = ci in shared.available_camera_indices
        btn_text = f"Cam {ci+1}"
        b2 = ctk.CTkButton(
            cam_row_ds,
            text=btn_text,
            width=100,
            height=32,
            font=("Arial", 10, "bold") if is_avail else ("Arial", 9),
            fg_color="#2ECC71" if ci == shared.current_camera_index else "#333333",
            text_color="black" if is_avail else "#666666",
            state="normal" if is_avail else "disabled",
            hover_color="#27AE60",
            corner_radius=6,
            command=lambda i=ci: select_cam_ds(i)
        )
        b2.pack(side="left", padx=2)
        ds_cam_btns[ci] = b2

    # ---------------- Target Role ----------------
    ctk.CTkLabel(controls_frame, text="Target Role:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 3))
    role_var = ctk.StringVar(value="Student")
    role_btn = ctk.CTkSegmentedButton(controls_frame, values=["Student", "Admin"], variable=role_var, 
                                      selected_color="#2ECC71", height=35)
    role_btn.pack(fill="x", padx=20, pady=(0, 15))

    # ---------------- ID / Registration ----------------
    id_lbl = ctk.CTkLabel(controls_frame, text="Student ID:", font=("Arial", 12))
    id_lbl.pack(anchor="w", padx=20, pady=(5,0))
    id_entry = ctk.CTkEntry(controls_frame, placeholder_text="e.g. 2023-08-16868")
    id_entry.pack(fill="x", padx=20, pady=(0, 15))

    def update_id_label(*args):
        id_lbl.configure(text=f"{role_var.get()} ID:")
    role_var.trace_add("write", update_id_label)

    # ---------------- Progress ----------------
    ctk.CTkLabel(controls_frame, text="Progress:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5,0))
    progress_bar = ctk.CTkProgressBar(controls_frame, progress_color="#2ECC71")
    progress_bar.pack(fill="x", padx=20, pady=(0, 5))
    progress_bar.set(0)

    status_label = ctk.CTkLabel(controls_frame, text="Ready", font=("Arial", 16, "bold"), text_color="white")
    status_label.pack(pady=10)


    instruction_label = ctk.CTkLabel(controls_frame, text="Enter ID to begin.", font=("Arial", 12, "italic"), text_color="#3498DB", wraplength=260)
    instruction_label.pack(pady=(0, 10))

    count_label = ctk.CTkLabel(controls_frame, text="0 / 500", font=("Arial", 14))
    count_label.pack(pady=5)

    # ---------------- ZIP UPLOAD UI (Inside zip_controls_frame) ----------------
    ctk.CTkLabel(
        zip_controls_frame,
        text="ZIP DATASET IMPORT",
        font=("Arial", 14, "bold"),
        text_color="gray"
    ).pack(pady=(10, 10))

    def select_zip_file():
        path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if path:
            zip_path_var.set(path)
            status_label.configure(text="ZIP Selected", text_color="#3498DB")
            instruction_label.configure(text=f"Ready to process: {os.path.basename(path)}", text_color="white")

    zip_path_var = ctk.StringVar(value="")
    ctk.CTkButton(zip_controls_frame, text="📁 CHOOSE ZIP FOLDER", fg_color="#34495E", hover_color="#2C3E50", command=select_zip_file).pack(fill="x", padx=20, pady=10)
    
    def start_zip_processing_thread():
        user_id = id_entry.get().strip()
        role = role_var.get()
        zip_path = zip_path_var.get()
        
        if not user_id:
            status_label.configure(text=f"Enter {role} ID!", text_color="red")
            return
        if not zip_path:
            status_label.configure(text="Select ZIP File!", text_color="red")
            return
            
        threading.Thread(target=process_zip_upload, args=(zip_path, user_id, role), daemon=True).start()

    btn_zip_process = ctk.CTkButton(
        zip_controls_frame,
        text="🚀 IMPORT & ALIGN DATASET",
        fg_color="#2ECC71",
        hover_color="#27AE60",
        height=45,
        font=("Arial", 14, "bold"),
        command=start_zip_processing_thread
    )
    btn_zip_process.pack(fill="x", padx=20, pady=20)

    def process_zip_upload(zip_path, user_id, role):
        nonlocal face_data
        try:
            status_label.configure(text="Processing...", text_color="white")
            progress_bar.set(0)
            face_data = []
            
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Find all image files
                img_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
                image_files = [f for f in z.namelist() if f.lower().endswith(img_exts) and not f.startswith('__MACOSX')]
                
                if not image_files:
                    status_label.configure(text="No images in ZIP!", text_color="red")
                    return
                
                total = len(image_files)
                processed_count = 0
                
                for i, img_path in enumerate(image_files):
                    try:
                        with z.open(img_path) as f:
                            data = f.read()
                            img_np = np.frombuffer(data, np.uint8)
                            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                            
                            if img is not None:
                                h_i, w_i = img.shape[:2]
                                yunet.setInputSize((w_i, h_i))
                                _, faces = yunet.detect(img)
                                
                                if faces is not None:
                                    # Pick biggest face
                                    faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                                    face = faces_sorted[0]
                                    
                                    # Align and Crop
                                    aligned = sface.alignCrop(img, face)
                                    if aligned is not None:
                                        face_data.append(aligned)
                                        processed_count += 1
                    except: continue
                    
                    # Update progress
                    perc = (i + 1) / total
                    progress_bar.set(perc)
                    count_label.configure(text=f"{len(face_data)} faces found")
                
                if len(face_data) > 0:
                    save_dataset() # Reuse existing save logic
                else:
                    status_label.configure(text="No faces found in images!", text_color="red")
        except Exception as e:
            status_label.configure(text="ZIP Error!", text_color="red")
            print(f"ZIP Error: {e}")



    # ---------------- CAPTURE STATE ----------------
    is_capturing = False
    is_paused = False
    face_data = []
    max_faces = 500
    current_stage = 0

    capture_stages = [
        {"target": 50,  "instruction": "Stage 1/10: Position yourself at a normal distance (Neutral)."},
        {"target": 100, "instruction": "Stage 2/10: Move FAR from the camera (Full face and shoulders visible)."},
        {"target": 150, "instruction": "Stage 3/10: Be CLOSE to the camera (Face fills the frame)."},
        {"target": 200, "instruction": "Stage 4/10: NEAR the camera: Turn your head slowly LEFT and RIGHT."},
        {"target": 250, "instruction": "Stage 5/10: NEAR the camera: Look slightly UP and DOWN (Chin movement)."},
        {"target": 300, "instruction": "Stage 6/10: FAR from the camera: Turn your head slowly LEFT and RIGHT."},
        {"target": 350, "instruction": "Stage 7/10: FAR from the camera: Look slightly UP and DOWN."},
        {"target": 400, "instruction": "Stage 8/10: Change your EXPRESSIONS (Smile, Blink, be serious)."},
        {"target": 450, "instruction": "Stage 9/10: Tilt your head LEFT and RIGHT (Ear toward shoulder)."},
        {"target": 500, "instruction": "Stage 10/10: FINAL PASS: Move naturally at various distances."}
    ]
    
    try:
        yunet_path = "dnn_model/face_detection_yunet.onnx"
        yunet = cv2.FaceDetectorYN.create(yunet_path, "", (320, 320))
        
        sface_path = "dnn_model/face_recognition_sface.onnx"
        sface = cv2.FaceRecognizerSF.create(sface_path, "")
    except Exception as e:
        print(f"Error loading YuNet or SFace model: {e}")
        yunet = None
        sface = None

    # ---------------- VIDEO LOOP ----------------
    def update_video_loop():
        nonlocal is_capturing, face_data, current_stage, is_paused

        if not content_area.winfo_exists():
            return

        cap = shared.camera_cap
        if cap is None or not cap.isOpened():
            if shared.start_camera_stream():
                shared.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                shared.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                shared.camera_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            content_area.after(100, update_video_loop)
            return

        ret, frame = cap.read()
        if not ret:
            content_area.after(10, update_video_loop)
            return

        display_frame = frame.copy()
        h_img, w_img = frame.shape[:2]

        if yunet is not None and sface is not None:
            yunet.setInputSize((w_img, h_img))
            _, faces = yunet.detect(frame)

            if faces is not None:
                # Prioritize biggest face by box area
                faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                face = faces_sorted[0]

                box = face[0:4].astype("int")
                (startX, startY, w, h) = box

                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w_img - 1, startX + w)
                endY = min(h_img - 1, startY + h)
                w = endX - startX
                h = endY - startY

                if w >= 60 and h >= 60:
                    aspect_ratio = w / h
                    if 0.75 <= aspect_ratio <= 1.3:
                        try:
                            # Perfectly align the face using YuNet's 5 physical landmarks
                            aligned_face = sface.alignCrop(frame, face)
                            
                            x, y = startX, startY

                            if is_capturing:
                                if aligned_face.mean() < 30:
                                    pass # Too dark
                                else:
                                    save_frame = True
                                    if len(face_data) > 0:
                                        similarities = [cv2.absdiff(f, aligned_face).mean() for f in face_data[-5:]]
                                        if min(similarities) < 8:
                                            save_frame = False
                                    
                                    if save_frame:
                                        face_data.append(aligned_face)
                                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 79, 255), 2)
                                
                                # Draw YuNet landmarks dynamically during capture
                                for i in range(5):
                                    pt = (int(face[4 + i*2]), int(face[5 + i*2]))
                                    cv2.circle(display_frame, pt, 2, (0, 255, 0), -1)
                            else:
                                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 79, 0), 2)
                        except Exception as align_e:
                            print(f"Alignment Error: {align_e}")

        if is_capturing:
            progress = len(face_data) / max_faces
            progress_bar.set(progress)
            count_label.configure(text=f"{len(face_data)} / {max_faces}")
            
            target = capture_stages[current_stage]["target"]
            if len(face_data) >= target:
                is_capturing = False
                if len(face_data) >= max_faces:
                    save_dataset()
                else:
                    is_paused = True
                    current_stage += 1
                    status_label.configure(text="PAUSED", text_color="#F39C12")
                    instruction_label.configure(text=capture_stages[current_stage]["instruction"], text_color="#F39C12")
                    btn_resume.pack(fill="x", padx=20, pady=(0, 60))


        img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        
        if not viewport.winfo_exists(): return
        view_w, view_h = (480, 360) if not responsive_manager.is_small() else (320, 240)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(view_w, view_h))
        viewport.configure(image=ctk_img)
        viewport.image = ctk_img



        content_area.after(10, update_video_loop)

    # ---------------- SAVE DATASET ----------------
    def save_dataset():
        user_id = id_entry.get().strip()
        role = role_var.get()
        folder = "train_images" if role == "Student" else "train_images_admin"

        if len(face_data) > 0:
            if not os.path.exists(folder):
                os.makedirs(folder)

            file_path = f"{folder}/{user_id}.npy"

            if os.path.exists(file_path):
                status_label.configure(
                    text=f"❌ {role} ID already exists!",
                    text_color="red"
                )
                face_data.clear()
                return

            data_arr = np.asarray(face_data).reshape((len(face_data), -1))
            np.save(file_path, data_arr)

            status_label.configure(text=f"Dataset saved for {user_id}", text_color="#2ECC71")
            instruction_label.configure(text="Capture complete! Now run training.", text_color="gray")
            face_data.clear()
            id_entry.delete(0, "end")

    # ---------------- START BUTTON ----------------
    def start_capture():
        nonlocal is_capturing, face_data, current_stage, is_paused
        user_id = id_entry.get().strip()
        role = role_var.get()
        folder = "train_images" if role == "Student" else "train_images_admin"

        if not user_id:
            status_label.configure(text=f"Enter a valid {role} ID!", text_color="red")
            return

        file_path = f"{folder}/{user_id}.npy"
        if os.path.exists(file_path):
            status_label.configure(
                text=f"❌ {role} ID already exists!",
                text_color="red"
            )
            return

        face_data = []
        current_stage = 0
        is_paused = False
        is_capturing = True
        
        status_label.configure(text="Capturing...", text_color="white")
        instruction_label.configure(text=capture_stages[0]["instruction"], text_color="#2ECC71")
        btn_resume.pack_forget()

    btn_start = ctk.CTkButton(
        controls_frame,
        text="▶ START CAPTURE",
        fg_color="#2ECC71",
        hover_color="#27AE60",
        height=45,
        font=("Arial", 14, "bold"),
        corner_radius=10,
        command=start_capture
    )
    btn_start.pack(fill="x", padx=20, pady=(0, 60))


    def resume_capture():
        nonlocal is_capturing, is_paused
        is_paused = False
        is_capturing = True
        status_label.configure(text="Capturing...", text_color="white")
        instruction_label.configure(text=capture_stages[current_stage]["instruction"], text_color="#2ECC71")
        btn_resume.pack_forget()

    btn_resume = ctk.CTkButton(
        controls_frame,
        text="▶ CONTINUE NEXT STAGE",
        fg_color="#F39C12",
        hover_color="#D68910",
        height=45,
        font=("Arial", 14, "bold"),
        corner_radius=10,
        command=resume_capture
    )
    # Initially hidden

    # ---------------- CLEANUP ----------------
    def on_cleanup(event=None):
        if event and event.widget != main_frame:
            return
        nonlocal is_capturing
        is_capturing = False
        shared.release_camera_stream()

    main_frame.bind("<Destroy>", on_cleanup)

    update_video_loop()