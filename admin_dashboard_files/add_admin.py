import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image
import re
from db import add_new_admin

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
        email = email_entry.get().strip()
        password = pass_entry.get().strip()
        
        # Validation checks
        if not full_name or not email or not password:
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
        success, msg = add_new_admin(full_name, email, password, final_image_path)
        
        if success:
            messagebox.showinfo("Success", msg)
            
            # Clear the form logic
            name_entry.delete(0, 'end')
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
                  command=handle_add_admin).pack(fill="x", pady=(20, 0))
