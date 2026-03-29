import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from PIL import Image
import re
from db import add_new_admin, get_all_admins

# Persistent state to remember form vs list view across dashboard refreshes
_view_state = {"current": "form"}

def show_add_admin_content(content_area, responsive_manager):
    """Add new admin users - FULLY IMPLEMENTED with sub-view persistence"""
    
    # Track the admin's profile picture if they choose one
    selected_image_path = None
    
    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 40
    wrap_len = 280 if is_small else 800

    # Dispatcher to handle whichever view is currently active
    if _view_state["current"] == "list":
        switch_to_admins_view(content_area, responsive_manager)
        return

    # --- REGISTRATION FORM VIEW ---
    # Clear current content area to start fresh
    for widget in content_area.winfo_children():
        widget.destroy()

    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=side_pad, pady=(30, 10))
    
    ctk.CTkLabel(header_frame, text="👤 Add Administrator", 
                 font=("Segoe UI", 24 if is_small else 34, "bold"), text_color="#3498DB",
                 wraplength=wrap_len).pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Create a new administrative account with full dashboard access.", 
                 font=("Segoe UI", 11 if is_small else 12), text_color="gray",
                 wraplength=wrap_len).pack(anchor="w", pady=(0, 20))


    # Form Container
    admin_frame = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=16, border_width=1, border_color="#333")
    admin_frame.pack(fill="x", expand=False, padx=side_pad, pady=10)
    
    # Grid vs Stacking inside the container
    inner_grid = ctk.CTkFrame(admin_frame, fg_color="transparent")
    inner_grid.pack(fill="x", expand=False, padx=15 if is_small else 40, pady=20 if is_small else 30)
    
    # --- LEFT COLUMN (Text Inputs) ---
    left_col = ctk.CTkFrame(inner_grid, fg_color="transparent")
    if is_small:
        left_col.pack(side="top", fill="x", pady=(0, 20))
    else:
        inner_grid.columnconfigure(0, weight=1)
        inner_grid.columnconfigure(1, weight=1)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
    
    ctk.CTkLabel(left_col, text="Administrator Details", font=("Arial", 16 if is_small else 18, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(anchor="w", pady=(0, 25))

    
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
    if is_small:
        right_col.pack(side="top", fill="x", pady=(0, 20))
    else:
        right_col.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
    
    ctk.CTkLabel(right_col, text="Profile Picture (Optional)", font=("Arial", 16 if is_small else 18, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(anchor="w", pady=(0, 25))
    
    photo_box = ctk.CTkFrame(right_col, fg_color="#121212", border_width=1, border_color="#444", corner_radius=10)
    photo_box.pack(fill="x", pady=(0, 20), ipadx=20, ipady=30 if not is_small else 15)

    
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
            
            # Clear the form
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
    
    # Switch handlers
    def reset_scroll():
        try:
            # Get the parent CTkScrollableFrame's canvas and reset scroll
            parent = content_area.master
            if hasattr(parent, "_parent_canvas"):
                parent._parent_canvas.yview_moveto(0)
        except:
            pass

    def go_to_list():
        _view_state["current"] = "list"
        reset_scroll()
        switch_to_admins_view(content_area, responsive_manager)

    # Place submit buttons at the bottom of the section
    btn_wrapper = left_col if not is_small else inner_grid
    ctk.CTkButton(btn_wrapper, text="➕ REGISTER ADMINISTRATOR", height=55 if is_small else 50, 
                  font=("Arial", 14, "bold"), fg_color="#2ECC71", hover_color="#27AE60", text_color="black", 
                  command=handle_add_admin).pack(fill="x", pady=(20, 10))

    ctk.CTkButton(btn_wrapper, text="👁️ VIEW REGISTERED ADMINS", height=55 if is_small else 50, 
                  font=("Arial", 14, "bold"), fg_color="#3498DB", hover_color="#2980B9", text_color="white", 
                  command=go_to_list).pack(fill="x", pady=(0, 60 if is_small else 0))


def switch_to_admins_view(content_area, responsive_manager):
    """Sub-view: List all registered administrators with AUTO-REFRESH"""
    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 40
    wrap_len = 280 if is_small else 800

    # Clear current content area
    for widget in content_area.winfo_children():
        widget.destroy()
        
    # Header for the View Admins page
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=side_pad, pady=(30, 20 if is_small else 10))
    
    def reset_scroll():
        try:
            parent = content_area.master
            if hasattr(parent, "_parent_canvas"):
                parent._parent_canvas.yview_moveto(0)
        except:
            pass

    # Back button
    def go_back():
        _view_state["current"] = "form"
        reset_scroll()
        # Clear and go back to registration form
        for widget in content_area.winfo_children():
            widget.destroy()
        show_add_admin_content(content_area, responsive_manager)

    ctk.CTkButton(header_frame, text="⬅️ BACK", height=40, width=80,
                  font=("Arial", 12 if is_small else 13, "bold"), fg_color="#333", hover_color="#444", 
                  command=go_back).pack(side="left")
                  
    ctk.CTkLabel(header_frame, text="Admin List", 
                 font=("Segoe UI", 20 if is_small else 28, "bold"), text_color="#3498DB",
                 wraplength=wrap_len).pack(side="left", padx=10)

    # REFRESH BUTTON
    def refresh_list():
        switch_to_admins_view(content_area, responsive_manager)

    ctk.CTkButton(header_frame, text="🔄", width=40, height=40, font=("Arial", 16),
                  fg_color="#3498DB", hover_color="#2980B9", command=refresh_list).pack(side="right", padx=5)
                 
    # Scrollable container workaround
    list_container = ctk.CTkFrame(content_area, fg_color="transparent")
    list_container.pack(fill="both", expand=True, padx=side_pad, pady=(0, 30))

    try:
        admins = get_all_admins()
        
        if not admins:
            ctk.CTkLabel(list_container, text="No administrators found.", text_color="gray", font=("Arial", 16)).pack(pady=40)
        else:
            for i, admin in enumerate(admins):
                card = ctk.CTkFrame(list_container, fg_color="#1f1f1f", corner_radius=10)
                is_last_item = (i == len(admins) - 1)
                card.pack(fill="x", padx=10, pady=10 if not is_last_item else (10, 80 if is_small else 10))
                
                name = admin.get('full_name') or admin.get('name') or admin.get('username') or "Admin"
                email = admin.get('email') or "No Email"
                reg_no = admin.get('registration_no') or "No Reg Number"
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=15 if is_small else 20, pady=15)
                
                ctk.CTkLabel(info_frame, text=name, font=("Arial", 16 if is_small else 18, "bold"), 
                            text_color="white", wraplength=wrap_len).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Reg No: {reg_no}\n{email}", font=("Arial", 12 if is_small else 14), 
                            text_color="#aaaaaa", wraplength=wrap_len, anchor="w", justify="left").pack(anchor="w", pady=(5, 0))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load administrative list: {str(e)}")

    # AUTO-REFRESH POLLER: Every 30 seconds, if the view state is still 'list', refresh
    def auto_refresh():
        # Only refresh if we are still on the list view and the window is alive
        if _view_state["current"] == "list" and content_area.winfo_exists():
            refresh_list()

    content_area.after(30000, auto_refresh)
