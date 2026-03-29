import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import shutil
import re
from db import get_connection

def show_register_student_content(content_area, responsive_manager):
    """
    Mount the student registration page natively inside the Admin Dashboard.
    """
    # Use a solid transparent frame instead of a scrollable one to avoid double-scrollbars
    # since the dashboard's main content area is already scrollable.
    # Clear previous widgets to prevent duplication/repetition
    for widget in content_area.winfo_children():
        widget.destroy()
        
    is_small = responsive_manager.is_small()

    side_pad = 10 if is_small else 30
    wrap_len = 280 if is_small else 800

    wrapper = ctk.CTkFrame(content_area, fg_color="transparent")
    wrapper.pack(fill="both", expand=True, padx=side_pad, pady=10)

    
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
    header_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
    header_frame.pack(fill="x", pady=(10, 20))
    ctk.CTkLabel(header_frame, text="Register New Student", text_color="#2ECC71", 
                 font=("Segoe UI", 22 if is_small else 28, "bold"),
                 wraplength=wrap_len).pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Add a new student profile to the facial recognition system.", 
                 text_color="gray", font=("Segoe UI", 11 if is_small else 12),
                 wraplength=wrap_len).pack(anchor="w")


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
                if con is None: return
                cursor = con.cursor()

                # Check duplicate registration number
                cursor.execute("SELECT 1 FROM students WHERE registration_no=%s", (reg_no,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Registration number is already taken.")
                    return

                # Check duplicate email
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

                messagebox.showinfo("Success", f"{entries['Full_Name'].get()} has been registered successfully!")
                clear_fields()

            except Exception as e:
                messagebox.showerror("Error", f"Submission error: {str(e)}")

            finally:
                if 'con' in locals():
                    con.close()

    # --- 4. UI CONSTRUCTION ---
    
    progress_wrapper = ctk.CTkFrame(wrapper, fg_color="transparent")
    progress_wrapper.pack(fill="x", pady=(0, 20))

    progress_bar = ctk.CTkProgressBar(progress_wrapper, height=8, progress_color="#2ECC71")
    progress_bar.pack(fill="x", side="left" if not is_small else "top", expand=True, pady=(0, 5) if is_small else 0)
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_wrapper, text="0%")
    progress_label.pack(side="right" if not is_small else "top", padx=10)


    # Main Grid (2 Columns)
    grid_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
    grid_frame.pack(fill="both", expand=True)
    
    col_side = "top" if is_small else "left"
    
    left_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
    left_col.pack(side=col_side, fill="both", expand=True, padx=(0, 20 if not is_small else 0))
    
    right_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
    right_col.pack(side=col_side, fill="both", expand=True)


    # Render inputs across two columns to save vertical space
    for idx, label_text in enumerate(labels_text):
        target_col = left_col if idx % 2 == 0 else right_col
        
        field_frame = ctk.CTkFrame(target_col, fg_color="transparent")
        field_frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(field_frame, text=label_text.replace("_", " "), text_color="gray", font=("Arial", 12, "bold"))
        lbl.pack(anchor="w")

        entry = ctk.CTkEntry(field_frame, height=40, placeholder_text=field_config[label_text], fg_color="#121212", border_color="#333", text_color="white")
        if "Password" in label_text:
            entry.configure(show="●")

        entry.pack(fill="x", pady=(2, 5))
        entry.bind("<KeyRelease>", update_progress)
        entries[label_text] = entry

    # Profile Image Section stretches across bottom
    image_section = ctk.CTkFrame(wrapper, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#333")
    image_section.pack(fill="x", pady=20)

    ctk.CTkLabel(image_section, text="Profile Image", font=("Arial", 14, "bold"), text_color="white").pack(pady=(15, 5))

    image_preview_label = ctk.CTkLabel(image_section, text="No Image Selected", width=100, height=100, fg_color="#2b2b2b", corner_radius=8)
    image_preview_label.pack(pady=5)

    image_status_label = ctk.CTkLabel(image_section, text="None", font=("Arial", 10), text_color="gray")
    image_status_label.pack()

    ctk.CTkButton(image_section, text="🖼️ BROWSE IMAGE", height=32, command=select_profile_image, fg_color="#3498DB", hover_color="#2980B9").pack(pady=(10, 15))

    btn_reg = ctk.CTkButton(wrapper, text="REGISTER STUDENT", font=("Arial", 16, "bold"), command=submit, fg_color="#2ECC71", hover_color="#27AE60", height=50)
    btn_reg.pack(fill="x", pady=(10, 60))

