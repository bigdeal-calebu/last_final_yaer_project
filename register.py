import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import shutil
import re
from header import create_header
from db import get_connection

def show_registration_page(root, on_user_login=None, on_admin_login=None, include_header=True):

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
    if include_header:
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

    # --- Responsive helpers (matched to header.py breakpoints) ---
    def _get_width():
        try:
            root.update_idletasks()
            return root.winfo_width()
        except Exception:
            return 800

    def _breakpoint(w):
        if w < 400:  return "tiny"
        if w < 600:  return "mobile"
        if w < 1000: return "tablet"
        return "desktop"

    if include_header:
        # Full-page standalone screen uses a heavy center-aligned shadow box
        shadow_frame = ctk.CTkFrame(root, fg_color="#0f0f0f", corner_radius=40)
        shadow_frame.pack(expand=True, fill="both", padx=30, pady=(2, 15), anchor="n") # Tighter top margin

        main_container = ctk.CTkFrame(shadow_frame, fg_color="#1f1f1f", corner_radius=30, border_width=2, border_color="#333333")
        main_container.pack(fill="both", expand=True, padx=12, pady=12)
    else:
        # Admin dashboard embeds directly without extra wrapping shadows
        shadow_frame = ctk.CTkFrame(root, fg_color="transparent")
        shadow_frame.pack(fill="both", expand=True)
        main_container = ctk.CTkFrame(shadow_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=8)

    title_label = ctk.CTkLabel(main_container, text="CREATE ACCOUNT", text_color="#2ECC71", font=("Segoe UI", 22, "bold"))
    title_label.pack(pady=(15, 8))

    progress_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
    progress_wrapper.pack(fill="x", padx=20, pady=(0, 15))

    progress_bar = ctk.CTkProgressBar(progress_wrapper, height=8, progress_color="#2ECC71")
    progress_bar.pack(fill="x", side="left", expand=True)
    progress_bar.set(0)

    progress_label = ctk.CTkLabel(progress_wrapper, text="0%")
    progress_label.pack(side="right", padx=8)

    # Always scrollable so content is accessible on any screen size
    scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=8)

    field_frames = []
    def _get_field_pady(width):
        return 2 if width < 400 else 4

    for label_text in labels_text:
        field_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        field_frame.pack(fill="x", pady=_get_field_pady(_get_width()))
        field_frames.append(field_frame)

        lbl = ctk.CTkLabel(field_frame, text=label_text.replace("_", " "), text_color="#cccccc", font=("Segoe UI", 11))
        lbl.pack(anchor="w", padx=8)

        entry = ctk.CTkEntry(field_frame, height=36, placeholder_text=field_config[label_text], font=("Segoe UI", 12))
        if "Password" in label_text:
            entry.configure(show="●")

        entry.pack(fill="x", padx=8, pady=(2, 4))
        entry.bind("<KeyRelease>", update_progress)
        entries[label_text] = entry

    image_section = ctk.CTkFrame(scroll_frame, fg_color="#1e1e1e", corner_radius=10)
    image_section.pack(fill="x", pady=12, padx=8)

    ctk.CTkLabel(image_section, text="Profile Image", text_color="white", font=("Segoe UI", 12, "bold")).pack(pady=5)

    image_preview_label = ctk.CTkLabel(image_section, text="No Image\nSelected", width=90, height=90, fg_color="#2b2b2b", corner_radius=8, font=("Segoe UI", 10))
    image_preview_label.pack(pady=5)

    image_status_label = ctk.CTkLabel(image_section, text="None", font=("Segoe UI", 10), wraplength=200)
    image_status_label.pack()

    ctk.CTkButton(image_section, text="Browse Image", command=select_profile_image, fg_color="#3498DB", hover_color="#2980B9", height=36, font=("Segoe UI", 12)).pack(pady=10, padx=20, fill="x")

    # --- Buttons live INSIDE the scroll frame so they are always reachable ---
    btn_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    btn_container.pack(fill="x", pady=(10, 20))

    btn_reg = ctk.CTkButton(btn_container, text="Register", command=submit, fg_color="#2ECC71", hover_color="#27AE60", height=44, font=("Segoe UI", 13, "bold"))

    # Only show 'Login' button if we are NOT inside the admin dashboard
    if include_header:
        btn_login = ctk.CTkButton(btn_container, text="Login", command=on_user_login, fg_color="#3498DB", hover_color="#2980B9", height=44, font=("Segoe UI", 13, "bold"))

    def adjust_button_layout(event):
        # Use scroll_frame width for accurate breakpoint (btn_container fills it)
        width = scroll_frame.winfo_width() or event.width
        btn_reg.pack_forget()
        if include_header: btn_login.pack_forget()

        if width < 600:
            # Small screens: stack buttons vertically, small side padding
            pad = 10 if width < 400 else 20
            btn_reg.pack(fill="x", padx=pad, pady=5)
            if include_header: btn_login.pack(fill="x", padx=pad, pady=5)
        else:
            if include_header:
                btn_reg.pack(side="left", expand=True, padx=15)
                btn_login.pack(side="right", expand=True, padx=15)
            else:
                btn_reg.pack(expand=True, padx=15)  # Center lone Register button

    btn_container.bind("<Configure>", adjust_button_layout)

    # --- 5. ROOT-LEVEL RESPONSIVE SCALING ---
    # Adjust outer paddings and title font as the window changes size
    def on_root_resize(event):
        if event.widget is not root:
            return
        w = event.width
        bp = _breakpoint(w)

        # Scale title font
        fs = {"tiny": 14, "mobile": 18, "tablet": 22, "desktop": 26}.get(bp, 22)
        title_label.configure(font=("Segoe UI", fs, "bold"))

        # Scale outer shadow padding (standalone mode only)
        # Scale outer shadow padding (standalone mode only)
        if include_header:
            h_pad = {"tiny": 2, "mobile": 8, "tablet": 15, "desktop": 25}.get(bp, 12)
            v_pad_bottom = {"tiny": 5, "mobile": 10, "tablet": 12, "desktop": 15}.get(bp, 12)
            anchor_pos = "n" if bp in ["tiny", "mobile"] else "center"
            # Use minimal top padding (2px) and scale bottom padding
            shadow_frame.pack_configure(padx=h_pad, pady=(2, v_pad_bottom), anchor=anchor_pos)

        # Scale field vertical padding
        f_pady = _get_field_pady(w)
        for ff in field_frames:
            ff.pack_configure(pady=f_pady)

        # Scale progress bar side padding
        p_pad = {"tiny": 4, "mobile": 8, "tablet": 14, "desktop": 18}.get(bp, 14)
        progress_wrapper.pack_configure(padx=p_pad)

    root.bind("<Configure>", on_root_resize, add="+")