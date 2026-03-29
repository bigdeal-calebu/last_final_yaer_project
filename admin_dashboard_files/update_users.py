import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image
from db import search_student, update_full_student_record, update_student_photo

def show_update_users_content(content_area, responsive_manager):
    """Update existing student records dynamically."""
    
    # Track who is currently selected
    current_student = {"original_reg_no": None, "new_photo_path": None}
    
    # Top static container for Header and Search Bar (Will not scroll)
    top_static_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    top_static_frame.pack(fill="x")

    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 30
    wrap_len = 250 if is_small else 800

    header_frame = ctk.CTkFrame(top_static_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=side_pad, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="✏️ Manage Student Records", 
                 font=("Segoe UI", 24 if is_small else 32, "bold"), text_color="#F39C12",
                 wraplength=wrap_len).pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Search for a student and modify their complete database profile.", 
                 font=("Segoe UI", 11 if is_small else 12), text_color="gray",
                 wraplength=wrap_len).pack(anchor="w", pady=(0, 20))


    # --- SEARCH SECTION (FIXED AT TOP) ---
    search_frame = ctk.CTkFrame(top_static_frame, fg_color="#1a1a1a", corner_radius=15)
    search_frame.pack(fill="x", padx=side_pad, pady=(0, 10), ipadx=20, ipady=15)
    
    search_col_mode = "top" if is_small else "left"
    search_row = ctk.CTkFrame(search_frame, fg_color="transparent")
    search_row.pack(fill="x", pady=10)
    
    ctk.CTkLabel(search_row, text="Search (Name / Reg No):", font=("Arial", 12, "bold"), text_color="white").pack(side=search_col_mode, padx=10, pady=(0, 5) if is_small else 0)
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(search_row, textvariable=search_var, width=300 if not is_small else 250, placeholder_text="e.g. John or REG-001...")
    search_entry.pack(side=search_col_mode, padx=10, pady=(0, 10) if is_small else 0)

    
    # Scrollable lower body for Results and the Edit Form
    body_scroll = ctk.CTkScrollableFrame(content_area, fg_color="transparent")
    body_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 20))
    
    results_container = ctk.CTkFrame(body_scroll, fg_color="transparent")
    # Will pack this dynamically when results are found
    
    def perform_search():
        term = search_var.get().strip()
        if not term:
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return
            
        results = search_student(term)
        
        # Clear old results
        for widget in results_container.winfo_children():
            widget.destroy()
            
        if not results:
            ctk.CTkLabel(results_container, text="No students found.", text_color="red").pack(pady=10)
            results_container.pack(fill="x", pady=10)
            return

        ctk.CTkLabel(results_container, text=f"Found {len(results)} matches. Click a student to edit:", text_color="gray").pack(pady=5)
        
        for student in results:
            row_frame = ctk.CTkFrame(results_container, fg_color="#2c2c2c", corner_radius=5)
            row_frame.pack(fill="x", padx=10, pady=3)
            
            info_text = f"{student.get('full_name')}  |  {student.get('registration_no')}  |  {student.get('department')} ({student.get('course')})"
            is_small = responsive_manager.is_small()
            ctk.CTkLabel(row_frame, text=info_text, text_color="white", font=("Arial", 11 if is_small else 13, "bold"), 
                         wraplength=200 if is_small else 800).pack(side="left" if not is_small else "top", padx=15, pady=10)
            
            edit_btn = ctk.CTkButton(row_frame, text="✏️ EDIT", width=80 if not is_small else 200, fg_color="#3498DB", hover_color="#2980B9", font=("Arial", 12, "bold"), text_color="white")
            edit_btn.configure(command=lambda s=student: load_student_into_form(s))
            edit_btn.pack(side="right" if not is_small else "top", padx=15, pady=10)
            
        results_container.pack(fill="x", pady=10)

    ctk.CTkButton(search_row, text="SEARCH", width=120 if not is_small else 250, fg_color="#F39C12", hover_color="#D68910", text_color="black", font=("Arial", 12, "bold"), command=perform_search).pack(side=search_col_mode, padx=10)

    search_entry.bind("<Return>", lambda e: perform_search())


    # --- EDIT FORM SECTION ---
    form_frame = ctk.CTkFrame(body_scroll, fg_color="#1a1a1a", corner_radius=15)
    # Don't pack the form_frame until a student is selected
    
    ctk.CTkLabel(form_frame, text="Update Student Profile", font=("Segoe UI", 24, "bold"), text_color="#F39C12").pack(anchor="w", padx=30, pady=(20, 5))
    ctk.CTkLabel(form_frame, text="Modify core database attributes. Leave password blank to keep the current one.", font=("Arial", 11), text_color="#7F8C8D").pack(anchor="w", padx=30, pady=(0, 20))
    
    # Responsive Grid vs Pack for Edit Form
    grid_container = ctk.CTkFrame(form_frame, fg_color="transparent")
    grid_container.pack(fill="x", padx=10 if is_small else 20, pady=10)
    
    # Left Column: Personal Info 
    personal_card = ctk.CTkFrame(grid_container, fg_color="#2c2c2c", corner_radius=12)
    if is_small:
        personal_card.pack(fill="x", pady=10)
    else:
        grid_container.grid_columnconfigure((0, 1), weight=1)
        personal_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    ctk.CTkLabel(personal_card, text="👤 Personal Details", font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 15))
    
    # Right Column: Academic Info
    academic_card = ctk.CTkFrame(grid_container, fg_color="#2c2c2c", corner_radius=12)
    if is_small:
        academic_card.pack(fill="x", pady=10)
    else:
        academic_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
    ctk.CTkLabel(academic_card, text="🎓 Academic Records", font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 15))


    # Define variables
    vars_dict = {
        'full_name': ctk.StringVar(),
        'registration_no': ctk.StringVar(),
        'email': ctk.StringVar(),
        'password': ctk.StringVar(),
        'department': ctk.StringVar(),
        'year_level': ctk.StringVar(),
        'course': ctk.StringVar(),
        'session': ctk.StringVar(),
        'contact_number': ctk.StringVar()
    }
    
    def create_padded_input(parent, label_text, var_key, placeholder="", is_password=False):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(wrapper, text=label_text, font=("Arial", 12, "bold"), text_color="#AAB7B8").pack(anchor="w")
        entry = ctk.CTkEntry(wrapper, textvariable=vars_dict[var_key], placeholder_text=placeholder, height=35, border_width=1, corner_radius=6)
        if is_password:
            entry.configure(show="●")
        entry.pack(fill="x", pady=(2, 0))
        return entry
        
    # Build Left Column Layout
    create_padded_input(personal_card, "Full Name", 'full_name', "e.g. John Doe")
    create_padded_input(personal_card, "Email Address", 'email', "student@university.edu")
    create_padded_input(personal_card, "Contact Number", 'contact_number', "07XXXXXXXX")
    create_padded_input(personal_card, "System Password", 'password', "Enter new password or leave blank", is_password=True)
    
    # Build Right Column Layout
    create_padded_input(academic_card, "Registration Number", 'registration_no', "e.g. 2023-08-16868")
    create_padded_input(academic_card, "Department", 'department', "e.g. ICT")
    create_padded_input(academic_card, "Course Program", 'course', "e.g. Bachelor of Computer Science")
    
    # Nested Grid / Stack for Year / Session
    nested_academic = ctk.CTkFrame(academic_card, fg_color="transparent")
    nested_academic.pack(fill="x", padx=20, pady=(0, 15))
    
    y_wrapper = ctk.CTkFrame(nested_academic, fg_color="transparent")
    y_wrapper.pack(side="top" if is_small else "left", fill="x", expand=True, padx=(0, 5 if not is_small else 0), pady=(0, 10 if is_small else 0))
    ctk.CTkLabel(y_wrapper, text="Year Level", font=("Arial", 12, "bold"), text_color="#AAB7B8").pack(anchor="w")
    ctk.CTkEntry(y_wrapper, textvariable=vars_dict['year_level'], height=35).pack(fill="x")
    
    s_wrapper = ctk.CTkFrame(nested_academic, fg_color="transparent")
    s_wrapper.pack(side="top" if is_small else "left", fill="x", expand=True, padx=(5 if not is_small else 0, 0))
    ctk.CTkLabel(s_wrapper, text="Session", font=("Arial", 12, "bold"), text_color="#AAB7B8").pack(anchor="w")
    ctk.CTkEntry(s_wrapper, textvariable=vars_dict['session'], height=35).pack(fill="x")


    
    # Identity & Photo Section (Bottom Row extending full width)
    photo_frame = ctk.CTkFrame(form_frame, fg_color="#2c2c2c", corner_radius=12)
    photo_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    photo_inner = ctk.CTkFrame(photo_frame, fg_color="transparent")
    photo_inner.pack(pady=20)
    
    ctk.CTkLabel(photo_inner, text="Biometric Profile Photo", font=("Arial", 14, "bold"), text_color="white").pack(pady=(0, 10))
    
    photo_preview = ctk.CTkLabel(photo_inner, text="No Photo", width=120, height=120, fg_color="#1a1a1a", corner_radius=12)
    photo_preview.pack(pady=5)
    
    def change_photo():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            current_student["new_photo_path"] = file_path
            try:
                img = Image.open(file_path)
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                photo_preview.configure(image=img_ctk, text="")
                photo_preview.image = img_ctk
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
                
    ctk.CTkButton(photo_inner, text="Upload Replacement", command=change_photo, fg_color="#3498DB", hover_color="#2980B9", corner_radius=6).pack(pady=(15, 0))


    # --- SAVE LOGIC ---
    def load_student_into_form(student):
        # Reveal the form if it was hidden
        form_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        current_student["original_reg_no"] = student.get("registration_no")
        current_student["new_photo_path"] = None # Reset pending photo
        
        # Populate variables
        for key in vars_dict.keys():
            val = student.get(key)
            vars_dict[key].set(str(val) if val is not None else "")
            
        # Load photo preview
        img_path = student.get("image_path")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                photo_preview.configure(image=img_ctk, text="")
                photo_preview.image = img_ctk
            except:
                photo_preview.configure(image=None, text="Image Error")
                photo_preview.image = None
        else:
            photo_preview.configure(image=None, text="No Image Found")
            photo_preview.image = None
            
        # Clear search results visually to focus on form
        results_container.pack_forget()

    def handle_save_changes():
        if not current_student["original_reg_no"]:
            return
            
        new_data = {key: var.get().strip() for key, var in vars_dict.items()}
        
        if not new_data["full_name"] or not new_data["registration_no"] or not new_data["email"]:
            messagebox.showerror("Error", "Name, Registration No, and Email are required.")
            return

        success, msg = update_full_student_record(current_student["original_reg_no"], new_data)
        if not success:
            messagebox.showerror("Update Error", msg)
            return
            
        new_reg_no = new_data["registration_no"]
            
        # Handle Photo upload if present
        if current_student["new_photo_path"]:
            try:
                image_folder = "students_images"
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                    
                ext = os.path.splitext(current_student["new_photo_path"])[1]
                safe_filename = new_reg_no.replace('-', '_')
                final_path = os.path.join(image_folder, f"{safe_filename}{ext}")
                
                shutil.copy(current_student["new_photo_path"], final_path)
                
                photo_success, photo_msg = update_student_photo(new_reg_no, final_path)
                if not photo_success:
                    messagebox.showwarning("Photo Warning", f"Record updated, but photo failed: {photo_msg}")
            except Exception as e:
                messagebox.showwarning("Photo Warning", f"Record updated, but photo failed to copy: {e}")
                
        messagebox.showinfo("Success", f"Successfully updated student: {new_data['full_name']}")
        hide_form()

    def hide_form():
        # Clear fields
        for var in vars_dict.values():
            var.set("")
        current_student["original_reg_no"] = None
        current_student["new_photo_path"] = None
        
        photo_preview.configure(image=None, text="No Photo")
        photo_preview.image = None
        
        # Hide form
        form_frame.pack_forget()
        
        # Clear search and results so the user starts fresh
        search_var.set("")
        for widget in results_container.winfo_children():
            widget.destroy()
        results_container.pack_forget()

    btn_container = ctk.CTkFrame(form_frame, fg_color="transparent")
    btn_container.pack(fill="x", padx=30, pady=(10, 60 if is_small else 30))
    
    btn_side = "top" if is_small else "left"
    ctk.CTkButton(btn_container, text="🔙 GO BACK", height=50, 
                 font=("Arial", 14, "bold"), fg_color="#E74C3C", hover_color="#C0392B",
                 text_color="white", command=hide_form).pack(side=btn_side, fill="x" if is_small else "none", expand=True, padx=(0, 10 if not is_small else 0), pady=(0, 10 if is_small else 0))

    ctk.CTkButton(btn_container, text="💾 SAVE ALL CHANGES", height=50, 
                 font=("Arial", 16, "bold"), fg_color="#2ECC71", hover_color="#27AE60",
                 text_color="black", command=handle_save_changes).pack(side=btn_side if not is_small else "top", fill="x" if is_small else "none", expand=True, padx=(10 if not is_small else 0, 0))

