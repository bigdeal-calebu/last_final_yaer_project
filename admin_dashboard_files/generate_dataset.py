import cv2
import os
import numpy as np
import time
import threading
from PIL import Image, ImageTk
import customtkinter as ctk
import admin_dashboard_files.shared as shared

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

    # ---------------- LEFT PANEL (CONTROLS) ----------------
    controls_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15, width=320)
    controls_frame.pack(side="left", fill="y", padx=(0, 20), pady=0)

    ctk.CTkLabel(
        controls_frame,
        text="CONFIGURATION",
        font=("Arial", 14, "bold"),
        text_color="gray"
    ).pack(pady=(20, 10))

    # ---------------- Camera Selection ----------------
    ctk.CTkLabel(controls_frame, text="Camera:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 3))
    cam_row_ds = ctk.CTkFrame(controls_frame, fg_color="transparent")
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

    count_label = ctk.CTkLabel(controls_frame, text="0 / 100", font=("Arial", 14))
    count_label.pack(pady=5)

    # ---------------- RIGHT PANEL ----------------
    camera_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15, width=480, height=360)
    camera_frame.pack(side="right", padx=15, pady=15)
    camera_frame.pack_propagate(False)

    viewport = ctk.CTkLabel(camera_frame, text="", fg_color="black")
    viewport.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- CAPTURE STATE ----------------
    is_capturing = False
    is_paused = False
    face_data = []
    max_faces = 100
    current_stage = 0

    capture_stages = [
        {"target": 5, "instruction": "Stage 1/20: Neutral face (looking straight)."},
        {"target": 10, "instruction": "Stage 2/20: Slight natural smile."},
        {"target": 15, "instruction": "Stage 3/20: Big smile (teeth visible)."},
        {"target": 20, "instruction": "Stage 4/20: Head turned slightly left (~15°)."},
        {"target": 25, "instruction": "Stage 5/20: Head turned more left (~30°)."},
        {"target": 30, "instruction": "Stage 6/20: Head turned slightly right (~15°)."},
        {"target": 35, "instruction": "Stage 7/20: Head turned more right (~30°)."},
        {"target": 40, "instruction": "Stage 8/20: Looking slightly up (Chin raised)."},
        {"target": 45, "instruction": "Stage 9/20: Looking slightly down (Chin lowered)."},
        {"target": 50, "instruction": "Stage 10/20: Tilt head left (Ear toward shoulder)."},
        {"target": 55, "instruction": "Stage 11/20: Tilt head right (Ear toward shoulder)."},
        {"target": 60, "instruction": "Stage 12/20: Eyes slightly closed / blinking."},
        {"target": 65, "instruction": "Stage 13/20: Serious face (No emotion)."},
        {"target": 70, "instruction": "Stage 14/20: Normal or Bright lighting."},
        {"target": 75, "instruction": "Stage 15/20: Low lighting / Dim environment. (Cover camera slightly)"},
        {"target": 80, "instruction": "Stage 16/20: Light from one side (Side shadow)."},
        {"target": 85, "instruction": "Stage 17/20: Change your background / move slightly."},
        {"target": 90, "instruction": "Stage 18/20: OPTIONAL: If you wear glasses, put them on. Else, stay neutral."},
        {"target": 95, "instruction": "Stage 19/20: OPTIONAL: Take glasses off. Else, stay neutral."},
        {"target": 100, "instruction": "Stage 20/20: Vary distance (Sit farther back, then move close)."}
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
                    btn_resume.pack(fill="x", padx=20, pady=(0, 15))

        img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        viewport.configure(image=img)
        viewport.image = img

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
    btn_start.pack(fill="x", padx=20, pady=(0, 15))

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