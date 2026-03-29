import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import cv2
import threading
import json
import numpy as np
from admin_dashboard_files.shared import start_camera_stream as _scs # not used but for safety
from admin_dashboard_files.face_recognition import reload_classifier, train_all_students_bg

def show_train_classifier_content(content_area, responsive_manager):
    for widget in content_area.winfo_children():
        widget.destroy()

    is_small = responsive_manager.is_small()
    side_pad = 15 if is_small else 50
    wrap_len = 250 if is_small else 400

    ctk.CTkLabel(content_area, text="Train Classifier", font=("Segoe UI", 24 if is_small else 28, "bold"),
                 text_color="#3498DB").pack(anchor="w", padx=side_pad, pady=(30, 20))

    id_card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    id_card.pack(fill="x", padx=side_pad, pady=(0, 10))


    ctk.CTkLabel(id_card, text="Student ID to Train",
                 font=("Arial", 14, "bold"), text_color="gray").pack(pady=(20, 5))
    ctk.CTkLabel(id_card, text="Enter the same ID used during Generate Dataset (e.g. 2023-08-16868)",
                 font=("Arial", 10), text_color="#555555", wraplength=wrap_len).pack(padx=20)


    id_row = ctk.CTkFrame(id_card, fg_color="transparent")
    id_row.pack(fill="x", padx=10 if is_small else 40, pady=(10, 20))


    train_id_entry = ctk.CTkEntry(id_row, placeholder_text="2023-08-16868",height=42, font=("Arial", 13))
    train_id_entry.pack(side="top" if is_small else "left", fill="x", expand=True, padx=(0, 10 if not is_small else 0), pady=(0, 10) if is_small else 0)


    def refresh_hint():
        base = "train_images"
        if os.path.isdir(base):
            student_ids = [f[:-4] for f in os.listdir(base) if f.endswith(".npy")]
            hint.configure(text="Available: " + ", ".join(student_ids) if student_ids else "No datasets found")
        else:
            hint.configure(text="No train_images folder found — generate dataset first")

    scan_btn = ctk.CTkButton(id_row, text="🔍 Scan", width=80, height=42,
                             fg_color="#333", hover_color="#444", command=refresh_hint)
    scan_btn.pack(side="top" if is_small else "left", fill="x" if is_small else "none")


    hint = ctk.CTkLabel(id_card, text="Click 🔍 Scan to see available student IDs",
                        font=("Arial", 10), text_color="#555", wraplength=wrap_len)
    hint.pack(pady=(0, 15), padx=20)


    card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    card.pack(fill="x", padx=side_pad, pady=10)


    ctk.CTkLabel(card, text="Training Status",
                 font=("Arial", 16, "bold"), text_color="gray").pack(pady=(20, 10))

    status_label = ctk.CTkLabel(card, text="Enter a Student ID and press Train.",
                                font=("Arial", 16 if is_small else 20), text_color="white", wraplength=220 if is_small else 400)
    status_label.pack(pady=10, padx=20)



    progress = ctk.CTkProgressBar(card, height=20, corner_radius=10, progress_color="#3498DB")
    progress.pack(fill="x", padx=40, pady=20)

    progress.set(0)

    info_label = ctk.CTkLabel(card,
        text="Data loaded from train_images/<student_id>.npy",
        font=("Arial", 12), text_color="gray", wraplength=wrap_len)
    info_label.pack(pady=(0, 20), padx=20)


    # ---------------- TRAINING THREAD ----------------
    def run_training_thread(student_id, file_path):
        import pickle
        try:
            data = np.load(file_path)
            total_samples = len(data)

            if total_samples == 0:
                content_area.after(0, lambda: messagebox.showerror(
                    "No Data", f"No data found in:\n{file_path}"))
                content_area.after(0, lambda: reset_ui("Error: No data found"))
                return

            try:
                recognizer = cv2.FaceRecognizerSF.create("dnn_model/face_recognition_sface.onnx", "")
            except Exception as e:
                content_area.after(0, lambda: reset_ui(f"Error loading SFace model: {e}"))
                return

            numeric_label = abs(hash(student_id)) % 100000
            embeddings = []

            for i, row in enumerate(data):
                try:
                    # New format: BGR 112x112
                    img_np = row.reshape((112, 112, 3)).astype("uint8")
                    feature = recognizer.feature(img_np)
                    embeddings.append(feature[0])
                except ValueError:
                    # Fallback for old 100x100 grayscale datasets
                    try:
                        img_np = row.reshape((100, 100)).astype("uint8")
                        img_colored = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
                        img_resized = cv2.resize(img_colored, (112, 112))
                        feature = recognizer.feature(img_resized)
                        embeddings.append(feature[0])
                    except:
                        continue
                except Exception:
                    continue

                if i % 10 == 0 or i == total_samples - 1:
                    prog_val = (i + 1) / total_samples
                    content_area.after(0, lambda v=prog_val: progress.set(v))
                    content_area.after(0, lambda v=i + 1, t=total_samples:
                        info_label.configure(text=f"Extracting 128D Features: {v}/{t}"))

            if not embeddings:
                content_area.after(0, lambda: reset_ui("Error: Could not extract features."))
                return

            # Construct Master Embedding
            master_embedding = np.mean(embeddings, axis=0)

            os.makedirs("models", exist_ok=True)
            db_path = "models/embeddings.pkl"
            db = {}
            if os.path.exists(db_path):
                with open(db_path, "rb") as f:
                    db = pickle.load(f)
            
            db[student_id] = master_embedding
            
            with open(db_path, "wb") as f:
                pickle.dump(db, f)

            content_area.after(0, lambda: finish_ui(student_id, total_samples))
            reload_classifier()

        except Exception as e:
            content_area.after(0, lambda: reset_ui(f"Error: {e}"))

    def reset_ui(msg):
        status_label.configure(text=msg, text_color="red")
        btn_train.configure(state="normal")
        progress.set(0)

    def finish_ui(student_id, count):
        status_label.configure(text="Training Complete!", text_color="#2ECC71")
        info_label.configure(text=f"Trained {count} images for {student_id}")
        progress.set(1.0)
        btn_train.configure(state="normal")

    def start_training():
        student_id = train_id_entry.get().strip()

        if not student_id:
            messagebox.showerror("Error", "Enter Student ID")
            return

        file_path = os.path.join("train_images", f"{student_id}.npy")

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Dataset not found")
            return

        btn_train.configure(state="disabled")
        threading.Thread(target=run_training_thread,
                         args=(student_id, file_path), daemon=True).start()

    btn_train = ctk.CTkButton(content_area, text="▶ TRAIN THIS STUDENT",
                               command=start_training, height=45 if is_small else 32)
    btn_train.pack(fill="x" if is_small else "none", padx=side_pad, pady=20)


    # ---------------- TRAIN ALL ----------------
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

        threading.Thread(target=train_all_students_bg, args=(_progress, _status, _done, _error), daemon=True).start()

    btn_train_all = ctk.CTkButton(content_area, text="🔄 TRAIN ALL STUDENTS",
                                  command=start_all_training, height=45 if is_small else 32)
    btn_train_all.pack(fill="x" if is_small else "none", padx=side_pad, pady=10)


    # ============================================================
    # 🔥 DELETE STUDENT FEATURE (ADDED WITHOUT REMOVING ANYTHING)
    # ============================================================

    delete_card = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    delete_card.pack(fill="x", padx=side_pad, pady=(20, 40))


    ctk.CTkLabel(delete_card, text="Delete Trained Student",
                 font=("Arial", 16, "bold"), text_color="#E74C3C", wraplength=wrap_len).pack(pady=(20, 5))


    delete_entry = ctk.CTkEntry(delete_card,
                               placeholder_text="Enter Registration Number",
                               height=40)
    delete_entry.pack(padx=40, pady=10, fill="x")

    delete_status = ctk.CTkLabel(delete_card, text="", text_color="gray")
    delete_status.pack(pady=(0, 10))

    def delete_student_data():
        student_id = delete_entry.get().strip()

        if not student_id:
            messagebox.showerror("Error", "Enter registration number")
            return

        confirm = messagebox.askyesno("Confirm",
                                     f"Delete all data for {student_id}?")

        if not confirm:
            return

        deleted = False

        # delete dataset
        path = os.path.join("train_images", f"{student_id}.npy")
        if os.path.exists(path):
            os.remove(path)
            deleted = True

        import pickle
        db_path = "models/embeddings.pkl"
        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                db = pickle.load(f)
            if student_id in db:
                del db[student_id]
                deleted = True
                with open(db_path, "wb") as f:
                    pickle.dump(db, f)

        # remove from label map
        reload_classifier()

        if deleted:
            delete_status.configure(text="Deleted successfully. Retrain required.",
                                    text_color="#2ECC71")
        else:
            delete_status.configure(text="No data found",
                                    text_color="#E74C3C")

    delete_btn = ctk.CTkButton(delete_card, text="🗑 DELETE INDIVIDUAL STUDENT",
                               command=delete_student_data,
                               fg_color="#E74C3C")
    delete_btn.pack(pady=10)

    def delete_all_students_data():
        confirm = messagebox.askyesno("WARNING", 
            "CRITICAL ACTION: Are you sure you want to delete ALL trained student data? This cannot be undone.", 
            icon="warning")
        if not confirm:
            return
            
        deleted_count = 0
        
        # Delete all .npy files in train_images
        if os.path.exists("train_images"):
            for f in os.listdir("train_images"):
                if f.endswith(".npy"):
                    os.remove(os.path.join("train_images", f))
                    deleted_count += 1
                    
        # Delete embeddings database
        if os.path.exists("models/embeddings.pkl"):
            os.remove("models/embeddings.pkl")
            
        # Delete old XML files
        if os.path.exists("models"):
            for f in os.listdir("models"):
                if f.endswith(".xml"):
                    os.remove(os.path.join("models", f))
                    
        # Clear legacy label map
        label_map_file = "models/label_map.json"
        if os.path.exists(label_map_file):
            os.remove(label_map_file)
                
        # Remove primary old classifier
        if os.path.exists("classifier.xml"):
            os.remove("classifier.xml")
            
        reload_classifier()
        
        if deleted_count > 0:
            delete_status.configure(text=f"Wiped {deleted_count} student records completely.", text_color="#2ECC71")
        else:
            delete_status.configure(text="No trained data found.", text_color="gray")

    delete_all_btn = ctk.CTkButton(delete_card, text="⚠️ DELETE ALL STUDENTS",
                               command=delete_all_students_data,
                               fg_color="#8E44AD", hover_color="#732D91")
    delete_all_btn.pack(pady=(5, 15))