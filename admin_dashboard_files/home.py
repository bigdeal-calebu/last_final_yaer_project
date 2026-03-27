# home_dashboard.py
import customtkinter as ctk
import os
from admin_dashboard_files import shared
from admin_dashboard_files.shared import present_student_ids, get_connection
from admin_dashboard_files import view_attendance
from admin_dashboard_files.shared import sync_attendance_from_db
from admin_dashboard_files.attendance_archiver import check_and_archive_attendance

def show_home_content(content_area, responsive_manager, admin_data=None, show_content_callback=None):
    # Clear existing widgets
    for widget in content_area.winfo_children():  
        widget.destroy()       

    # handle daily archiving once
    check_and_archive_attendance()

    # Shared stats labels references for live updates
    stat_labels = {}

    # Header
    ctk.CTkLabel(content_area, text="Dashboard Overview", 
                 font=("Segoe UI", 28, "bold"), text_color="#3b9dd8").pack(anchor="w", padx=30, pady=(30, 20))
    
    # Statistics Cards
    stats_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    stats_frame.pack(fill="x", padx=30, pady=20)

    # Ensure stats are completely up-to-date initially
    shared.refresh_global_stats()
    
    # Use global cached stats
    total_students = shared.total_students_count
    current_present = len(shared.present_student_ids)
    current_absent = max(0, total_students - current_present)


    stats_data = [
        ("Total Students", str(total_students), "#3b9dd8", "👥"),
        ("Present Today", str(current_present), "#00c853", "✓"),
        ("Absent Today", str(current_absent), "#9c27b0", "✗")
    ]
    
    for label, value, color, icon in stats_data:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", border_width=2, 
                            border_color=color, corner_radius=12, height=130)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=f"{icon} {label}", text_color="#888888", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        val_label = ctk.CTkLabel(card, text=value, text_color=color, font=("Arial", 40, "bold"))
        val_label.pack(pady=5)
        stat_labels[label] = val_label

    def update_live_stats():
        """Updates the home stats in real-time when recognition occurs."""
        try:
            if not content_area.winfo_exists(): return
            
            p_count = len(shared.present_student_ids)
            t_count = shared.total_students_count
            a_count = max(0, t_count - p_count)
            
            if "Total Students" in stat_labels:
                stat_labels["Total Students"].configure(text=str(t_count))
            if "Present Today" in stat_labels:
                stat_labels["Present Today"].configure(text=str(p_count))
            if "Absent Today" in stat_labels:
                stat_labels["Absent Today"].configure(text=str(a_count))
        except:
            pass

    shared.sidebar_stats_callback = update_live_stats

    # -------------------- DATABASE POLLING (Cross-process Support) --------------------
    def poll_database_updates():
        """Periodically syncs with DB to catch updates from other processes/windows."""
        try:
            if not content_area.winfo_exists(): return
            
            # 1. Refresh ALL global stats (Attendance + Database)
            shared.refresh_global_stats()
            
            # Instantly update UI numbers on every refresh cycle
            update_live_stats()
            
            # 2. Live-Sync Today's Excel Archives
            from admin_dashboard_files.attendance_archiver import sync_live_excel
            from datetime import datetime
            sync_live_excel(datetime.now().strftime("%Y-%m-%d"))
            
            # 3. Schedule next check (every 5 seconds)
            content_area.after(5000, poll_database_updates)
        except:
            pass

    # Start polling
    content_area.after(2000, poll_database_updates)
    
    responsive_manager.register_grid(stats_frame, 3)

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

    responsive_manager.register_grid(buttons_frame, 3)