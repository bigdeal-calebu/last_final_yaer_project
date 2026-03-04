import customtkinter as ctk
from tkinter import messagebox
from db import search_student, get_student_by_regno, update_student_photo # and others if needed

def show_update_users_content(content_area, responsive_manager):
    """Update existing student records"""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="✏️ Update Student Records", 
                 font=("Segoe UI", 32, "bold"), text_color="#F39C12").pack(anchor="w")

    update_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    update_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    # Search Section
    search_row = ctk.CTkFrame(update_frame, fg_color="transparent")
    search_row.pack(fill="x", padx=30, pady=(30, 20))
    
    ctk.CTkLabel(search_row, text="Search Student (Reg No):", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
    search_entry = ctk.CTkEntry(search_row, width=250, placeholder_text="Enter Reg No...")
    search_entry.pack(side="left", padx=5)
    ctk.CTkButton(search_row, text="SEARCH", width=100, fg_color="#F39C12", text_color="black").pack(side="left", padx=10)
    
    # Edit Form
    form_frame = ctk.CTkFrame(update_frame, fg_color="#2c2c2c", corner_radius=10)
    form_frame.pack(fill="x", padx=30, pady=10)
    
    ctk.CTkLabel(form_frame, text="Edit Details", font=("Arial", 14, "bold"), text_color="darkorange").pack(anchor="w", padx=20, pady=(15, 10))
    
    # Name
    ctk.CTkLabel(form_frame, text="Full Name:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5, 0))
    name_entry = ctk.CTkEntry(form_frame, width=350)
    name_entry.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Email
    ctk.CTkLabel(form_frame, text="Email Address:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5, 0))
    email_entry = ctk.CTkEntry(form_frame, width=350)
    email_entry.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Course
    ctk.CTkLabel(form_frame, text="Course:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(5, 0))
    course_opt = ctk.CTkOptionMenu(form_frame, values=["Computer Science", "Engineering", "Mathematics", "Biology"], width=250)
    course_opt.pack(anchor="w", padx=20, pady=(0, 20))
    
    def handle_update():
        messagebox.showinfo("Success", "Student record updated successfully!")
        
    ctk.CTkButton(update_frame, text="💾 SAVE CHANGES", height=45, width=200, 
                 font=("Arial", 14, "bold"), fg_color="#2ECC71", text_color="black", command=handle_update).pack(pady=30)
