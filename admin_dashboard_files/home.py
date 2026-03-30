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

    # handle daily archiving once (in background)
    shared.run_in_background(check_and_archive_attendance)


    # Shared stats labels references for live updates
    stat_labels = {}

    # Header
    title_pad = responsive_manager.pad(15, 20, 25, 30)
    title_font = responsive_manager.font("page_title", "bold")
    ctk.CTkLabel(content_area, text="Dashboard Overview", 
                 font=title_font, text_color="#3b9dd8").pack(anchor="w", padx=title_pad, pady=(30, 10))

    
    # Statistics Cards
    stats_pad = responsive_manager.pad(10, 15, 20, 30)
    stats_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    stats_frame.pack(fill="x", padx=stats_pad, pady=10)


    # Ensure stats are completely up-to-date (in background)
    shared.run_in_background(shared.refresh_global_stats)

    
    # Use daily stats for accurate Today numbers
    from db import get_daily_system_stats
    total_students, current_present, current_absent = get_daily_system_stats()

    # Calculate Recognition Days
    from admin_dashboard_files import config_manager
    from datetime import datetime
    start_date_str = config_manager.get("starting_date")
    recognition_days = "0"
    if start_date_str:
        try:
            s_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            recognition_days = str((datetime.now().date() - s_dt).days + 1)
        except: pass

    stats_data = [
        ("Total Students", str(total_students), "#3b9dd8", "👥"),
        ("Today's Present", str(current_present), "#00c853", "✓"),
        ("Today's Absent", str(current_absent), "#9c27b0", "✗"),
        ("TOTAL DAYS FROM START", recognition_days, "#3498db", "🗓️")
    ]
    
    card_h = responsive_manager.pad(100, 110, 120, 130)
    val_fs = responsive_manager.fs("name")
    
    for label, value, color, icon in stats_data:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", border_width=2, 
                            border_color=color, corner_radius=12, height=card_h)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=f"{icon} {label}", text_color="#888888", font=("Arial", 10 if responsive_manager.is_small() else 12, "bold")).pack(pady=(15, 2))
        val_label = ctk.CTkLabel(card, text=value, text_color=color, font=("Arial", val_fs, "bold"))
        val_label.pack(pady=2)
        stat_labels[label] = val_label


    def update_live_stats():
        """Updates the home stats in real-time when recognition occurs."""
        try:
            if not content_area.winfo_exists(): return
            
            from db import get_daily_system_stats
            t_count, p_count, a_count = get_daily_system_stats()
            
            if "Total Students" in stat_labels:
                stat_labels["Total Students"].configure(text=str(t_count))
            if "Today's Present" in stat_labels:
                stat_labels["Today's Present"].configure(text=str(p_count))
            if "Today's Absent" in stat_labels:
                stat_labels["Today's Absent"].configure(text=str(a_count))
        except:
            pass

    shared.sidebar_stats_callback = update_live_stats

    # -------------------- DATABASE POLLING (Cross-process Support) --------------------
    def poll_database_updates():
        """Periodically syncs with DB to catch updates from other processes/windows."""
        try:
            if not content_area.winfo_exists(): return
            
            # 1. Refresh ALL global stats in background to avoid blocking polling
            shared.run_in_background(shared.refresh_global_stats, callback=lambda _: update_live_stats())

            
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
    
    responsive_manager.register_grid(stats_frame, 4)

    # Action Buttons
    btn_pad = responsive_manager.pad(10, 15, 20, 30)
    buttons_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=btn_pad, pady=10)

    
    def on_view_present_click():
        if show_content_callback:
            show_content_callback(view_attendance.show_present_list_content)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Wait", "Recognition system is loading. Please try again.")

    btn_h = responsive_manager.pad(40, 45, 50, 55)
    btn_font = responsive_manager.font("body_bold")

    btn1 = ctk.CTkButton(buttons_frame, text="🔍 View Present", fg_color="#00c853", 
                         hover_color="#00a844", height=btn_h, font=btn_font,
                         corner_radius=10, text_color="white", 
                         command=lambda: show_content_callback(view_attendance.show_present_list_content) if show_content_callback else None)
    
    btn2 = ctk.CTkButton(buttons_frame, text="❌ View Absent", fg_color="#9c27b0", 
                         hover_color="#7b1fa2", height=btn_h, font=btn_font,
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(view_attendance.show_absent_list_content) if show_content_callback else None)
    
    from db import get_all_students_full
    btn3 = ctk.CTkButton(buttons_frame, text="👥 View All Students", fg_color="darkorange", 
                         hover_color="#ff7700", height=btn_h, font=btn_font,
                         corner_radius=10, text_color="white",
                         command=lambda: show_content_callback(view_attendance.show_all_students_list_content, data_loader=get_all_students_full) if show_content_callback else None)



    responsive_manager.register_grid(buttons_frame, 3)