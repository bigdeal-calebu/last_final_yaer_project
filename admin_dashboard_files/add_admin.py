import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image
import re
from db import add_new_admin, get_all_admins

def show_add_admin_content(content_area, responsive_manager):
    """Add new admin users - FULLY IMPLEMENTED"""
    
    # Track the admin's profile picture if they choose one
    selected_image_path = None
    
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=40, pady=(30, 10))
    
    ctk.CTkLabel(header_frame, text="👤 Add New Administrator", 
                 font=("Segoe UI", 34, "bold"), text_color="#3498DB").pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Create a new administrative account with full dashboard access.", 
                 font=("Segoe UI", 12), text_color="gray").pack(anchor="w", pady=(0, 20))

    # Form Container
    admin_frame = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=16, border_width=1, border_color="#333")
    admin_frame.pack(fill="both", expand=True, padx=40, pady=10)
    
    # 2-Column Grid Layout inside the container
    inner_grid = ctk.CTkFrame(admin_frame, fg_color="transparent")
    inner_grid.pack(fill="both", expand=True, padx=40, pady=30)
    inner_grid.columnconfigure(0, weight=1)
    inner_grid.columnconfigure(1, weight=1)
    
    # --- LEFT COLUMN (Text Inputs) ---
    left_col = ctk.CTkFrame(inner_grid, fg_color="transparent")
    left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
    
    ctk.CTkLabel(left_col, text="Administrator Details", font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", pady=(0, 25))
    
    ctk.CTkLabel(left_col, text="Full Name", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    name_entry = ctk.CTkEntry(left_col, height=45, placeholder_text="e.g. John Doe", fg_color="#121212", border_color="#444", text_color="white")
    name_entry.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(left_col, text="Registration Number", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    reg_entry = ctk.CTkEntry(left_col, height=45, placeholder_text="e.g. ADM-2024-001", fg_color="#121212", border_color="#444", text_color="white")
    reg_entry.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(left_col, text="Email Address", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    email_entry = ctk.CTkEntry(left_col, height=45, placeholder_text="admin@university.edu", fg_color="#121212", border_color="#444", text_color="white")
    email_entry.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(left_col, text="Password", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    pass_entry = ctk.CTkEntry(left_col, height=45, placeholder_text="Create a secure password", show="●", fg_color="#121212", border_color="#444", text_color="white")
    pass_entry.pack(fill="x", pady=(0, 10))
    
    # --- RIGHT COLUMN (Photo Upload) ---
    right_col = ctk.CTkFrame(inner_grid, fg_color="transparent")
    right_col.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
    
    ctk.CTkLabel(right_col, text="Profile Picture (Optional)", font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", pady=(0, 25))
    
    photo_box = ctk.CTkFrame(right_col, fg_color="#121212", border_width=1, border_color="#444", corner_radius=10)
    photo_box.pack(fill="x", pady=(0, 20), ipadx=20, ipady=30)
    
    image_preview_label = ctk.CTkLabel(photo_box, text="No Photo Selected", width=150, height=150, fg_color="#2b2b2b", corner_radius=10)
    image_preview_label.pack(pady=(10, 15))
    
    image_status_label = ctk.CTkLabel(photo_box, text="JPG or PNG formats only", font=("Arial", 11), text_color="gray")
    image_status_label.pack(pady=(0, 15))

    def select_profile_image():
        nonlocal selected_image_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            selected_image_path = file_path
            img = Image.open(file_path)
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
            image_preview_label.configure(image=img_ctk, text="")
            image_preview_label.image = img_ctk
            image_status_label.configure(text=f"Selected: {os.path.basename(file_path)}", text_color="#3498DB")

    ctk.CTkButton(photo_box, text="🖼️ BROWSE IMAGE", height=40, font=("Arial", 12, "bold"), 
                  fg_color="#3498DB", hover_color="#2980B9", command=select_profile_image).pack()

    # --- SUBMIT BUTTON ---
    def handle_add_admin():
        nonlocal selected_image_path
        
        full_name = name_entry.get().strip()
        reg_no = reg_entry.get().strip()
        email = email_entry.get().strip()
        password = pass_entry.get().strip()
        
        # Validation checks
        if not full_name or not reg_no or not email or not password:
            messagebox.showerror("Validation Error", "Please fill out all required text fields.")
            return
            
        if len(password) < 6:
            messagebox.showerror("Validation Error", "Password must be at least 6 characters long.")
            return
            
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            messagebox.showerror("Validation Error", "Please enter a valid email address.")
            return

        # Prepare image copying if one was selected
        final_image_path = None
        if selected_image_path:
            image_folder = "admin_images"
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
                
            ext = os.path.splitext(selected_image_path)[1]
            # Use the first part of the email as the safe filename
            safe_filename = email.split('@')[0].replace('.', '_').lower()
            final_image_path = os.path.join(image_folder, f"admin_{safe_filename}{ext}")
            
            try:
                shutil.copy(selected_image_path, final_image_path)
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to save image: {e}")
                return

        # Save to database
        success, msg = add_new_admin(full_name, email, reg_no, password, final_image_path)
        
        if success:
            messagebox.showinfo("Success", msg)
            
            # Clear the form logic
            name_entry.delete(0, 'end')
            reg_entry.delete(0, 'end')
            email_entry.delete(0, 'end')
            pass_entry.delete(0, 'end')
            
            selected_image_path = None
            image_preview_label.configure(image=None, text="No Photo Selected")
            image_preview_label.image = None
            image_status_label.configure(text="JPG or PNG formats only", text_color="gray")
        else:
            messagebox.showerror("Database Error", msg)
    
    # Place submit button at the bottom of the left column to align with text fields
    ctk.CTkButton(left_col, text="➕ REGISTER ADMINISTRATOR", height=50, 
                  font=("Arial", 14, "bold"), fg_color="#2ECC71", hover_color="#27AE60", text_color="black", 
                  command=handle_add_admin).pack(fill="x", pady=(20, 10))

    def switch_to_admins_view():
        # Clear the current content area
        for widget in content_area.winfo_children():
            widget.destroy()
            
        # Header for the View Admins page
        header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 10))
        
        # Back button
        def go_back():
            for widget in content_area.winfo_children():
                widget.destroy()
            show_add_admin_content(content_area, responsive_manager)

        ctk.CTkButton(header_frame, text="⬅️ BACK", height=40, width=100,
                      font=("Arial", 13, "bold"), fg_color="#333", hover_color="#444", 
                      command=go_back).pack(side="left")
                      
        ctk.CTkLabel(header_frame, text="   👥 Registered Administrators", 
                     font=("Segoe UI", 28, "bold"), text_color="#3498DB").pack(side="left", padx=10)
                     
        # Scrollable list container
        scroll_frame = ctk.CTkScrollableFrame(content_area, fg_color="#121212", corner_radius=15, border_width=1, border_color="#333")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=(10, 30))
        
        admins = get_all_admins()
        
        if not admins:
            ctk.CTkLabel(scroll_frame, text="No administrators found.", text_color="gray", font=("Arial", 16)).pack(pady=40)
            return
            
        for admin in admins:
            card = ctk.CTkFrame(scroll_frame, fg_color="#1f1f1f", corner_radius=10)
            card.pack(fill="x", padx=20, pady=10)
            
            name = admin.get('full_name') or admin.get('name') or admin.get('username') or "Admin"
            email = admin.get('email', 'No Email')
            reg_no = admin.get('registration_no', 'No Reg No')
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
            
            ctk.CTkLabel(info_frame, text=name, font=("Arial", 18, "bold"), text_color="white").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Reg No: {reg_no} | Email: {email}", font=("Arial", 14), text_color="#aaaaaa").pack(anchor="w", pady=(5, 0))

    ctk.CTkButton(left_col, text="👁️ VIEW REGISTERED ADMINS", height=50, 
                  font=("Arial", 14, "bold"), fg_color="#3498DB", hover_color="#2980B9", text_color="white", 
                  command=switch_to_admins_view).pack(fill="x")
