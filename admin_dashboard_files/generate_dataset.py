import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import cv2
from admin_dashboard_files.shared import switch_camera_live, current_camera_index, start_camera_stream, face_cascade

def show_generate_dataset_content(content_area, responsive_manager):
    from admin_dashboard_files import shared # Local import to avoid circular dependency if any

    ctk.CTkLabel(content_area, text="Generate Dataset", font=("Segoe UI", 28, "bold"), text_color="#2ECC71").pack(anchor="w", padx=30, pady=(30, 20))
    
    main_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=30, pady=10)
    
    controls_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15, width=320)
    controls_frame.pack(side="left", fill="y", padx=(0, 20), pady=0)
    
    ctk.CTkLabel(controls_frame, text="CONFIGURATION", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(20, 10))

    ctk.CTkLabel(controls_frame, text="Camera:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 3))
    cam_row_ds = ctk.CTkFrame(controls_frame, fg_color="transparent")
    cam_row_ds.pack(fill="x", padx=20, pady=(0, 12))

    ds_cam_btns = {}

    def select_cam_ds(idx):
        switch_camera_live(idx)
        for i, b in ds_cam_btns.items():
            b.configure(fg_color="#2ECC71" if i == idx else "#333333")

    for ci in range(3):
        b2 = ctk.CTkButton(
            cam_row_ds, text=f"Cam {ci}",
            width=62, height=28, font=("Arial", 10, "bold"),
            fg_color="#2ECC71" if ci == shared.current_camera_index else "#333333",
            hover_color="#27AE60", corner_radius=6,
            command=lambda i=ci: select_cam_ds(i)
        )
        b2.pack(side="left", padx=2)
        ds_cam_btns[ci] = b2

    ctk.CTkLabel(controls_frame, text="Student ID:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5,0))
    id_entry = ctk.CTkEntry(controls_frame, placeholder_text="e.g. 2023-08-16868")
    id_entry.pack(fill="x", padx=20, pady=(0, 15))

    btn_start = ctk.CTkButton(controls_frame, text="▶ START CAPTURE", command=lambda: start_capture(),
                             fg_color="#2ECC71", hover_color="#27AE60", height=45,
                             font=("Arial", 14, "bold"), corner_radius=10)
    btn_start.pack(fill="x", padx=20, pady=(0, 15))

    ctk.CTkLabel(controls_frame, text="Format: YYYY-MM-NNNNN", font=("Arial", 10), text_color="#555555").pack(anchor="w", padx=20, pady=(0, 10))

    ctk.CTkLabel(controls_frame, text="Progress:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5,0))
    progress_bar = ctk.CTkProgressBar(controls_frame, progress_color="#2ECC71")
    progress_bar.pack(fill="x", padx=20, pady=(0, 5))
    progress_bar.set(0)
    
    status_label = ctk.CTkLabel(controls_frame, text="Ready", font=("Arial", 16, "bold"), text_color="white")
    status_label.pack(pady=10)
    
    count_label = ctk.CTkLabel(controls_frame, text="0 / 60", font=("Arial", 14))
    count_label.pack(pady=5)

    TOTAL_PHOTOS = 60
    DIRECTION_PHASES = [
        (0,  10, "😐  Look STRAIGHT at camera"),
        (10, 20, "⬅️  Slowly turn LEFT"),
        (20, 30, "➡️  Slowly turn RIGHT"),
        (30, 40, "⬆️  Tilt head UP"),
        (40, 50, "⬇️  Tilt head DOWN"),
        (50, 60, "🔄  Move in any direction"),
    ]

    guide_label = ctk.CTkLabel(
        controls_frame, text="Press START and follow instructions",
        font=("Arial", 11, "bold"), text_color="#F39C12",
        wraplength=260, justify="center"
    )
    guide_label.pack(padx=15, pady=(10, 5))

    def get_phase_instruction(count):
        for start, end, msg in DIRECTION_PHASES:
            if start <= count < end: return msg
        return "✅  Done!"

    camera_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15)
    camera_frame.pack(side="right", fill="both", expand=True)
    
    viewport = ctk.CTkLabel(camera_frame, text="", fg_color="black", height=400)
    viewport.pack(fill="both", expand=True, padx=15, pady=15)
    
    placeholder = ctk.CTkLabel(viewport, text="Initializing Camera...", text_color="#666666", font=("Arial", 18, "bold"))
    placeholder.place(relx=0.5, rely=0.5, anchor="center")

    capture_state = {"capturing": False, "count": 0, "student_id": ""}
    loop_active = [True]
    
    def on_stop():
        loop_active[0] = False
    
    content_area.stop_camera_loop = on_stop

    PAD_TOP    = 0.55
    PAD_SIDES  = 0.45
    PAD_BOTTOM = 0.50

    def expand_face_roi(x, y, w, h, img_h, img_w):
        pad_top    = int(h * PAD_TOP)
        pad_side   = int(w * PAD_SIDES)
        pad_bottom = int(h * PAD_BOTTOM)
        x1 = max(0, x - pad_side)
        y1 = max(0, y - pad_top)
        x2 = min(img_w, x + w + pad_side)
        y2 = min(img_h, y + h + pad_bottom)
        return x1, y1, x2, y2

    def update_capture_frame():
        if not loop_active: return
        try:
            if shared.camera_cap is None or not shared.camera_cap.isOpened():
                start_camera_stream()

            success, frame = shared.camera_cap.read()
            if success:
                img_h, img_w = frame.shape[:2]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                gray_eq = clahe.apply(gray)

                faces = face_cascade.detectMultiScale(
                    gray_eq, scaleFactor=1.05, minNeighbors=8, minSize=(80, 80),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                if len(faces) > 0:
                    fx, fy, fw, fh = max(faces, key=lambda r: r[2] * r[3])
                    x1, y1, x2, y2 = expand_face_roi(fx, fy, fw, fh, img_h, img_w)

                    box_color = (0, 255, 0) if capture_state["capturing"] else (0, 220, 255)
                    cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), box_color, 2)

                    if capture_state["capturing"] and capture_state["count"] < TOTAL_PHOTOS:
                        capture_state["count"] += 1
                        cnt       = capture_state["count"]
                        student_id = capture_state["student_id"]
                        save_dir = os.path.join("train_images", student_id)
                        os.makedirs(save_dir, exist_ok=True)
                        region_bgr = frame[y1:y2, x1:x2].copy()
                        if region_bgr.size > 0:
                            save_img   = cv2.resize(region_bgr, (200, 200), interpolation=cv2.INTER_LANCZOS4)
                            file_name  = os.path.join(save_dir, f"face_{cnt:03d}.jpg")
                            cv2.imwrite(file_name, save_img, [cv2.IMWRITE_JPEG_QUALITY, 95])

                        cv2.putText(frame, f"{cnt}/{TOTAL_PHOTOS}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                        count_label.configure(text=f"{cnt} / {TOTAL_PHOTOS}")
                        progress_bar.set(cnt / TOTAL_PHOTOS)
                        guide_label.configure(text=get_phase_instruction(cnt))

                        if cnt >= TOTAL_PHOTOS:
                            capture_state["capturing"] = False
                            status_label.configure(text="COMPLETE!", text_color="#2ECC71")
                            guide_label.configure(text=f"✅ All {TOTAL_PHOTOS} photos saved!")
                            messagebox.showinfo("Dataset Complete", f"✅ {TOTAL_PHOTOS} photos captured!")
                            btn_start.configure(state="normal", text="▶ START CAPTURE")

                    display_frame = frame
                else:
                    display_frame = frame.copy()
                    cv2.putText(display_frame, "Position your face in frame", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

                if placeholder.winfo_ismapped(): placeholder.place_forget()

                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Use a static UI scale fit to prevent bouncing window layout issues
                img = Image.fromarray(cv2.resize(frame_rgb, (640, 480), interpolation=cv2.INTER_LINEAR))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
                viewport.configure(image=ctk_img)
                viewport.image = ctk_img
        except Exception as e:
            import traceback
            print(f"Camera Loop Error in generate_dataset: {e}")
            traceback.print_exc()

        if loop_active[0] and content_area.winfo_exists():
            viewport.after(30, update_capture_frame)

    def start_capture():
        raw_id = id_entry.get().strip()
        if not raw_id:
            messagebox.showerror("Missing ID", "Please enter a Student ID first.")
            return
        save_dir = os.path.join("train_images", raw_id)
        if os.path.exists(save_dir) and len(os.listdir(save_dir)) > 0:
            if not messagebox.askyesno("Folder Exists", "Dataset already exists. Add more?"): return
        capture_state["student_id"] = raw_id
        capture_state["count"]      = 0
        capture_state["capturing"]  = True
        status_label.configure(text="CAPTURING...", text_color="#3498DB")
        guide_label.configure(text=get_phase_instruction(0))
        progress_bar.set(0)
        count_label.configure(text=f"0 / {TOTAL_PHOTOS}")
        btn_start.configure(state="disabled", text="⏳ Running...")

    update_capture_frame()
