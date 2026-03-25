import cv2
import os
import numpy as np
import time
import threading
from PIL import Image, ImageTk
import customtkinter as ctk
import admin_dashboard_files.shared as shared

def show_generate_dataset_content(content_area, responsive_manager):

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

    # ---------------- Student ID ----------------
    ctk.CTkLabel(controls_frame, text="Student ID:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5,0))
    id_entry = ctk.CTkEntry(controls_frame, placeholder_text="e.g. 2023-08-16868")
    id_entry.pack(fill="x", padx=20, pady=(0, 15))

    # ---------------- Progress ----------------
    ctk.CTkLabel(controls_frame, text="Progress:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5,0))
    progress_bar = ctk.CTkProgressBar(controls_frame, progress_color="#2ECC71")
    progress_bar.pack(fill="x", padx=20, pady=(0, 5))
    progress_bar.set(0)

    status_label = ctk.CTkLabel(controls_frame, text="Ready", font=("Arial", 16, "bold"), text_color="white")
    status_label.pack(pady=10)

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
    face_data = []
    max_faces = 100
    face_cascade = cv2.CascadeClassifier("cascade/haarcascade_frontalface_default.xml")

    # ---------------- VIDEO LOOP ----------------
    def update_video_loop():
        nonlocal is_capturing, face_data

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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=8,
            minSize=(40, 40)
        )

        for (x, y, w, h) in faces:
            if w < 60 or h < 60:
                continue

            aspect_ratio = w / h
            if aspect_ratio < 0.75 or aspect_ratio > 1.3:
                continue

            crop = frame[y:y+h, x:x+w]
            face_gray = cv2.resize(crop, (100, 100))
            face_gray = cv2.cvtColor(face_gray, cv2.COLOR_BGR2GRAY)
            face_gray = cv2.equalizeHist(face_gray)

            if is_capturing:
                if face_gray.mean() < 50:
                    continue
                if len(face_data) > 0:
                    similarities = [cv2.absdiff(f, face_gray).mean() for f in face_data[-5:]]
                    if min(similarities) < 8:
                        continue
                face_data.append(face_gray)
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 79, 255), 2)
            else:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 79, 0), 2)

        if is_capturing:
            progress = len(face_data) / max_faces
            progress_bar.set(progress)
            count_label.configure(text=f"{len(face_data)} / {max_faces}")
            if len(face_data) >= max_faces:
                is_capturing = False
                save_dataset()

        img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        viewport.configure(image=img)
        viewport.image = img

        content_area.after(10, update_video_loop)

    # ---------------- SAVE DATASET ----------------
    def save_dataset():
        student_id = id_entry.get().strip()
        if len(face_data) > 0:
            if not os.path.exists("train_images"):
                os.makedirs("train_images")

            file_path = f"train_images/{student_id}.npy"

            # ✅ ADDED: BLOCK DUPLICATE SAVE
            if os.path.exists(file_path):
                status_label.configure(
                    text="❌ Student ID already exists! Use another ID.",
                    text_color="red"
                )
                face_data.clear()
                return

            data_arr = np.asarray(face_data).reshape((len(face_data), -1))
            if os.path.exists(file_path):
                old_data = np.load(file_path)
                data_arr = np.vstack((old_data, data_arr))
            np.save(file_path, data_arr)

            status_label.configure(text=f"Dataset saved for {student_id}", text_color="#2ECC71")
            face_data.clear()
            id_entry.delete(0, "end")

    # ---------------- START BUTTON ----------------
    def start_capture():
        nonlocal is_capturing, face_data
        student_id = id_entry.get().strip()

        if not student_id:
            status_label.configure(text="Enter a valid Student ID!", text_color="red")
            return

        # ✅ ADDED: BLOCK DUPLICATE BEFORE CAPTURE
        file_path = f"train_images/{student_id}.npy"
        if os.path.exists(file_path):
            status_label.configure(
                text="❌ Student ID already exists! Use another ID.",
                text_color="red"
            )
            return

        face_data = []
        is_capturing = True
        status_label.configure(text="Capturing...", text_color="white")

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

    # ---------------- CLEANUP ----------------
    def on_cleanup(event=None):
        if event and event.widget != main_frame:
            return
        nonlocal is_capturing
        is_capturing = False
        shared.release_camera_stream()

    main_frame.bind("<Destroy>", on_cleanup)

    update_video_loop()