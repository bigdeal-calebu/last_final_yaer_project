import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import cv2
import threading
import numpy as np
from admin_dashboard_files.shared import LABEL_MAP_PATH, reload_classifier, load_label_map, train_all_students_bg

def show_train_classifier_content(content_area, responsive_manager):

    ctk.CTkLabel(content_area, text="Train Classifier", font=("Segoe UI", 28, "bold"),
                 text_color="#3498DB").pack(anchor="w", padx=30, pady=(30, 20))

    id_card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    id_card.pack(fill="x", padx=50, pady=(0, 10))

    ctk.CTkLabel(id_card, text="Student ID to Train",
                 font=("Arial", 14, "bold"), text_color="gray").pack(pady=(20, 5))
    ctk.CTkLabel(id_card, text="Enter the same ID used during Generate Dataset (e.g. 2023-08-16868)",
                 font=("Arial", 10), text_color="#555555").pack()

    id_row = ctk.CTkFrame(id_card, fg_color="transparent")
    id_row.pack(fill="x", padx=40, pady=(10, 20))

    train_id_entry = ctk.CTkEntry(id_row, placeholder_text="2023-08-16868",
                                  height=42, font=("Arial", 13))
    train_id_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def refresh_hint():
        base = "train_images"
        if os.path.isdir(base):
            folders = [f for f in os.listdir(base)
                       if os.path.isdir(os.path.join(base, f))]
            hint.configure(text="Available: " + ", ".join(folders) if folders else "No datasets found")
        else:
            hint.configure(text="No train_images folder found — generate dataset first")

    scan_btn = ctk.CTkButton(id_row, text="🔍 Scan", width=80, height=42,
                             fg_color="#333", hover_color="#444", command=refresh_hint)
    scan_btn.pack(side="left")

    hint = ctk.CTkLabel(id_card, text="Click 🔍 Scan to see available student IDs",
                        font=("Arial", 10), text_color="#555")
    hint.pack(pady=(0, 15))

    card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    card.pack(fill="x", padx=50, pady=10)

    ctk.CTkLabel(card, text="Training Status",
                 font=("Arial", 16, "bold"), text_color="gray").pack(pady=(20, 10))
    status_label = ctk.CTkLabel(card, text="Enter a Student ID and press Train.",
                                font=("Arial", 20), text_color="white")
    status_label.pack(pady=10)

    progress = ctk.CTkProgressBar(card, width=400, height=20,
                                  corner_radius=10, progress_color="#3498DB")
    progress.pack(pady=20)
    progress.set(0)

    info_label = ctk.CTkLabel(card,
                              text="Images will be loaded from  train_images/<student_id>/",
                              font=("Arial", 12), text_color="gray")
    info_label.pack(pady=(0, 20))

    def run_training_thread(student_id, data_dir):
        try:
            image_files = [
                os.path.join(data_dir, f)
                for f in os.listdir(data_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            total_files = len(image_files)

            if total_files == 0:
                content_area.after(0, lambda: messagebox.showerror(
                    "No Data", f"No images found in:\n{data_dir}\n\nPlease generate a dataset first."))
                content_area.after(0, lambda: reset_ui("Error: No images found"))
                return

            faces, ids = [], []
            numeric_label = abs(hash(student_id)) % 100000

            for i, image_path in enumerate(image_files):
                try:
                    img_gray = Image.open(image_path).convert("L")
                    img_np   = np.array(img_gray, "uint8")
                    faces.append(img_np)
                    ids.append(numeric_label)
                except Exception:
                    continue

                if i % 5 == 0 or i == total_files - 1:
                    prog_val = (i + 1) / total_files
                    content_area.after(0, lambda v=prog_val: progress.set(v))
                    content_area.after(0, lambda v=i + 1, t=total_files: info_label.configure(text=f"Processing image {v} of {t}..."))

            content_area.after(0, lambda: status_label.configure(text="Training model...", text_color="#F39C12"))

            clf = cv2.face.LBPHFaceRecognizer_create()
            clf.train(faces, np.array(ids))

            os.makedirs("models", exist_ok=True)
            per_student_path = os.path.join("models", f"{student_id}.xml")
            clf.save(per_student_path)
            clf.save("classifier.xml")

            try:
                existing_map = {}
                if os.path.exists(LABEL_MAP_PATH):
                    with open(LABEL_MAP_PATH, "r") as f:
                        existing_map = json.load(f)
                existing_map[str(numeric_label)] = student_id
                with open(LABEL_MAP_PATH, "w") as f:
                    json.dump(existing_map, f, indent=2)
            except Exception as map_err:
                print(f"Warning: could not save label_map.json: {map_err}")

            content_area.after(0, lambda: finish_ui(student_id, total_files))
            reload_classifier()
            load_label_map()

        except Exception as e:
            content_area.after(0, lambda err=str(e): reset_ui(f"Error: {err}"))

    def reset_ui(msg):
        status_label.configure(text=msg, text_color="red")
        btn_train.configure(state="normal", text="▶ TRAIN THIS STUDENT")
        progress.set(0)

    def finish_ui(student_id, count):
        status_label.configure(text="Training Complete!", text_color="#2ECC71")
        info_label.configure(
            text=f"✅  Trained on {count} images for student  {student_id}\n"
                 f"Model saved → classifier.xml  |  models/{student_id}.xml")
        progress.set(1.0)
        messagebox.showinfo("Training Complete",
            f"✅  Model trained successfully!\n\nStudent ID : {student_id}\nImages used: {count}\n"
            f"Saved to   : classifier.xml")
        btn_train.configure(state="normal", text="▶ START TRAINING")

    def start_training():
        student_id = train_id_entry.get().strip()
        if not student_id:
            messagebox.showerror("Missing ID", "Please enter the Student ID you want to train.")
            return
        data_dir = os.path.join("train_images", student_id)
        if not os.path.isdir(data_dir):
            messagebox.showerror("Folder Not Found", f"No dataset folder found for:\n{student_id}")
            return
        btn_train.configure(state="disabled", text="⏳ Training...")
        status_label.configure(text=f"Loading images for {student_id}...", text_color="#3498DB")
        progress.set(0)
        info_label.configure(text=f"Reading from  train_images/{student_id}/")
        t = threading.Thread(target=run_training_thread, args=(student_id, data_dir))
        t.daemon = True
        t.start()

    btn_train = ctk.CTkButton(content_area, text="▶ TRAIN THIS STUDENT", command=start_training,
                               height=50, width=220, font=("Arial", 14, "bold"),
                               fg_color="#3498DB", hover_color="#2980B9", corner_radius=10)
    btn_train.pack(pady=(25, 8))

    def start_all_training():
        btn_train_all.configure(state="disabled", text="⏳ Training All...")
        status_label.configure(text="Scanning all student folders...", text_color="#3498DB")
        progress.set(0)
        info_label.configure(text="Loading all train_images subfolders...")

        def _progress(p, msg):
            content_area.after(0, lambda: (progress.set(p), info_label.configure(text=msg)))

        def _status(msg):
            content_area.after(0, lambda: status_label.configure(text=msg, text_color="#F39C12"))

        def _done(n_students, n_imgs):
            content_area.after(0, lambda: (
                status_label.configure(text="All Students Trained!", text_color="#2ECC71"),
                info_label.configure(text=f"✅ {n_students} students | {n_imgs} images"),
                progress.set(1.0),
                btn_train_all.configure(state="normal", text="🔄 TRAIN ALL STUDENTS"),
                messagebox.showinfo("Training Complete", f"✅ Combined model trained!\n\nStudents: {n_students}\nImages: {n_imgs}")))

        def _error(msg):
            content_area.after(0, lambda: reset_ui(f"Error: {msg}"))

        t = threading.Thread(target=train_all_students_bg, args=(_progress, _status, _done, _error), daemon=True)
        t.start()

    btn_train_all = ctk.CTkButton(content_area, text="🔄 TRAIN ALL STUDENTS", command=start_all_training,
                                  height=50, width=220, font=("Arial", 14, "bold"),
                                  fg_color="#2ECC71", hover_color="#27AE60", corner_radius=10)
    btn_train_all.pack(pady=(0, 25))
    ctk.CTkLabel(content_area, text="💡 Train All trains every student at once.",
                 font=("Arial", 10), text_color="#555555", wraplength=500).pack()
