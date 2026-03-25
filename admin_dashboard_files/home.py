# home_dashboard.py
import customtkinter as ctk
import os
from admin_dashboard_files.shared import present_student_ids, get_connection
from admin_dashboard_files import view_attendance

def show_home_content(content_area, responsive_manager, admin_data=None, show_content_callback=None):
    # Clear existing widgets
    for widget in content_area.winfo_children():  
        widget.destroy()       

    # Header
    ctk.CTkLabel(content_area, text="Dashboard Overview", 
                 font=("Segoe UI", 28, "bold"), text_color="#3b9dd8").pack(anchor="w", padx=30, pady=(30, 20))
    
    # Statistics Cards
    stats_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    stats_frame.pack(fill="x", padx=30, pady=20)

    # Database query for total students
    total_students = 0
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            result = cursor.fetchone()
            total_students = result[0] if result else 0
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Database query error: {e}")
        total_students = 0
    
    current_present = len(present_student_ids)
    current_absent = max(0, total_students - current_present)

    unknown_count = 0
    if os.path.exists("unknowns"):
        unknown_count = len([d for d in os.listdir("unknowns") if os.path.isdir(os.path.join("unknowns", d))])

    stats_data = [
        ("Total Students", str(total_students), "#3b9dd8", "👥"),
        ("Present Today", str(current_present), "#00c853", "✓"),
        ("Absent Today", str(current_absent), "#9c27b0", "✗"),
        ("Captured Unknowns", str(unknown_count), "#ff5722", "👤"),
    ]
    
    for label, value, color, icon in stats_data:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", border_width=2, 
                            border_color=color, corner_radius=12, height=130)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=f"{icon} {label}", text_color="#888888", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, text_color=color, font=("Arial", 40, "bold")).pack(pady=5)
    
    responsive_manager.register_grid(stats_frame, 4)

    # Action Buttons
    buttons_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=30, pady=20)
    
    def on_view_present_click():
        if show_content_callback:
            show_content_callback(view_attendance.show_present_list_content)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Wait", "Recognition system is loading. Please try again.")

    btn1 = ctk.CTkButton(buttons_frame, text="🔍 View Present", fg_color="#00c853", 
                         hover_color="#00a844", height=55, font=("Arial", 15, "bold"),
                         corner_radius=10, text_color="white", 
                         command=on_view_present_click)
    
    btn2 = ctk.CTkButton(buttons_frame, text="❌ View Absent", fg_color="#9c27b0", 
                         hover_color="#7b1fa2", height=55, font=("Arial", 15, "bold"),
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(view_attendance.show_absent_list_content) if show_content_callback else None)
    
    btn3 = ctk.CTkButton(buttons_frame, text="👥 View All Students", fg_color="darkorange", 
                         hover_color="#ff7700", height=55, font=("Arial", 15, "bold"),
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(view_attendance.show_all_students_list_content) if show_content_callback else None)

    btn4 = ctk.CTkButton(buttons_frame, text="🕵️ View Unknowns", fg_color="#ff5722", 
                         hover_color="#e64a19", height=55, font=("Arial", 15, "bold"),
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(lambda a, r: view_attendance.show_unknowns_list_content(a, r, show_content_callback=show_content_callback)) if show_content_callback else None)

    btn5 = ctk.CTkButton(buttons_frame, text="📂 All Files", fg_color="#3b9dd8", 
                         hover_color="#2980b9", height=55, font=("Arial", 15, "bold"),
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(view_attendance.show_attendance_content) if show_content_callback else None)
    
    responsive_manager.register_grid(buttons_frame, 5)