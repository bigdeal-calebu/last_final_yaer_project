import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import shutil
import re
from header import create_header
from db import get_connection

def show_registration_page(root, on_user_login=None, on_admin_login=None):

    # --- 1. SETTINGS & CONFIG ---
    field_config = {
        "Full_Name": "e.g. John Doe",
        "Registration_No": "e.g. 2023-08-16868",
        "Email": "example@email.com",
        "Password": "Enter secure password",
        "ConfirmPassword": "Repeat password",
        "Department": "e.g. ICT",
        "Year": "e.g. 1",
        "Course": "e.g. BSIT",
        "Session": "e.g. Day",
        "Phone_No": "e.g. 07XXXXXXXX"
    }

    labels_text = list(field_config.keys())
    entries = {}
    selected_image_path = None

    # --- 2. HEADER ---
    header = create_header(root, title_text="Smart Attendance System", subtitle_text="Student Registration")
    header.pack(fill="x", side="top")

    # --- 3. LOGIC FUNCTIONS ---

    def select_profile_image():
        nonlocal selected_image_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            selected_image_path = file_path
            img = Image.open(file_path)
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            image_preview_label.configure(image=img_ctk, text="")
            image_preview_label.image = img_ctk
            image_status_label.configure(text=os.path.basename(file_path), text_color="#2ECC71")
            update_progress()

    def update_progress(event=None):
        filled = sum(1 for e in entries.values() if e.get().strip() != "")
        if selected_image_path:
            filled += 1
        total = len(labels_text) + 1
        percent = filled / total
        progress_bar.set(percent)
        progress_label.configure(text=f"{int(percent*100)}%")

    def validation():
        for label, entry in entries.items():
            if entry.get().strip() == "":
                messagebox.showerror("Error", f"{label.replace('_', ' ')} is required")
                return False

        if not selected_image_path:
            messagebox.showerror("Error", "Please select a profile image")
            return False

        full_name = entries["Full_Name"].get().strip()
        if len(full_name.split()) < 2 or not all(x.isalpha() or x.isspace() for x in full_name):
            messagebox.showerror("Error", "Full Name must be letters only (min 2 words).")
            return False

        reg_no = entries["Registration_No"].get().strip()
        if not re.match(r"^\d{4}-\d{2}-\d{5}$", reg_no):
            messagebox.showerror("Error", "Invalid Registration Format. Use: 2023-08-16868")
            return False

        email = entries["Email"].get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return False

        if len(entries["Password"].get()) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.")
            return False

        if entries["Password"].get() != entries["ConfirmPassword"].get():
            messagebox.showerror("Error", "Passwords do not match.")
            return False

        if not entries["Year"].get().isdigit():
            messagebox.showerror("Error", "Year must be a number.")
            return False

        phone = entries["Phone_No"].get().strip()
        if not (phone.isdigit() and len(phone) == 10 and phone.startswith("07")):
            messagebox.showerror("Error", "Phone must be 10 digits starting with 07.")
            return False

        return True

    def clear_fields():
        nonlocal selected_image_path
        for entry in entries.values():
            entry.delete(0, "end")

        selected_image_path = None
        image_preview_label.configure(image=None, text="No Image Selected")
        image_preview_label.image = None
        image_status_label.configure(text="None", text_color="white")
        progress_bar.set(0)
        progress_label.configure(text="0%")

    def submit():
        if validation():
            try:
                image_folder = "students_images"
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)

                reg_no = entries["Registration_No"].get().strip()
                email = entries["Email"].get().strip()

                con = get_connection()
                cursor = con.cursor()

                # ✅ Check duplicate registration number
                cursor.execute("SELECT 1 FROM students WHERE registration_no=%s", (reg_no,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Registration number is already taken.")
                    return

                # ✅ Check duplicate email
                cursor.execute("SELECT 1 FROM students WHERE email=%s", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Email is already taken.")
                    return

                ext = os.path.splitext(selected_image_path)[1]
                safe_filename = reg_no.replace('-', '_')
                final_path = os.path.join(image_folder, f"{safe_filename}{ext}")

                shutil.copy(selected_image_path, final_path)

                query = """INSERT INTO students 
                (full_name, registration_no, email, password, confirm_password, 
                department, year_level, course, session, contact_number, image_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                data_values = [entries[label].get() for label in labels_text]
                data_values.append(final_path)

                cursor.execute(query, tuple(data_values))
                con.commit()

                messagebox.showinfo("Success", "You have been registered successfully!")
                clear_fields()

                if on_user_login:
                    on_user_login(data_values)

            except Exception as e:
                messagebox.showerror("Error", f"Submission error: {str(e)}")

            finally:
                if 'con' in locals():
                    con.close()

    # --- 4. UI CONSTRUCTION ---
    shadow_frame = ctk.CTkFrame(root, fg_color="#0f0f0f", corner_radius=40)
    shadow_frame.pack(expand=True, fill="both", padx=60, pady=20)

    main_container = ctk.CTkFrame(shadow_frame, fg_color="#1f1f1f", corner_radius=30, border_width=2, border_color="#333333")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)

    title_label = ctk.CTkLabel(main_container, text="CREATE ACCOUNT", text_color="#2ECC71", font=("Segoe UI", 26, "bold"))
    title_label.pack(pady=(20, 10))

    progress_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
    progress_wrapper.pack(fill="x", padx=40, pady=(0, 20))

    progress_bar = ctk.CTkProgressBar(progress_wrapper, height=8, progress_color="#2ECC71")
    progress_bar.pack(fill="x", side="left", expand=True)
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_wrapper, text="0%")
    progress_label.pack(side="right", padx=10)

    scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20)

    for label_text in labels_text:
        field_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        field_frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(field_frame, text=label_text.replace("_", " "), text_color="white")
        lbl.pack(anchor="w", padx=10)

        entry = ctk.CTkEntry(field_frame, height=35, placeholder_text=field_config[label_text])
        if "Password" in label_text:
            entry.configure(show="●")

        entry.pack(fill="x", padx=10, pady=(2, 5))
        entry.bind("<KeyRelease>", update_progress)
        entries[label_text] = entry

    image_section = ctk.CTkFrame(scroll_frame, fg_color="#1e1e1e", corner_radius=10)
    image_section.pack(fill="x", pady=15, padx=10)

    ctk.CTkLabel(image_section, text="Profile Image", text_color="white").pack(pady=5)

    image_preview_label = ctk.CTkLabel(image_section, text="No Image Selected", width=100, height=100, fg_color="#2b2b2b", corner_radius=8)
    image_preview_label.pack(pady=5)

    image_status_label = ctk.CTkLabel(image_section, text="None", font=("Arial", 10))
    image_status_label.pack()

    ctk.CTkButton(image_section, text="Browse Image", command=select_profile_image, fg_color="#3498DB", hover_color="#2980B9").pack(pady=10)

    btn_container = ctk.CTkFrame(main_container, fg_color="transparent")
    btn_container.pack(fill="x", pady=20)

    btn_reg = ctk.CTkButton(btn_container, text="Register", command=submit, fg_color="#2ECC71", hover_color="#27AE60", height=45)
    btn_login = ctk.CTkButton(btn_container, text="Login", command=on_admin_login, fg_color="#3498DB", hover_color="#2980B9", height=45)

    def adjust_button_layout(event):
        width = event.width
        btn_reg.pack_forget()
        btn_login.pack_forget()
        if width < 600:
            btn_reg.pack(fill="x", padx=40, pady=5)
            btn_login.pack(fill="x", padx=40, pady=5)
        else:
            btn_reg.pack(side="left", expand=True, padx=20)
            btn_login.pack(side="right", expand=True, padx=20)

    btn_container.bind("<Configure>", adjust_button_layout)