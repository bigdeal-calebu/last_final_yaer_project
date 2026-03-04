import customtkinter as ctk
from PIL import Image
import os
import time
from admin_dashboard_files.shared import present_details_list, present_student_ids, get_connection
from db import get_attendance_history

def show_attendance_content(content_area, responsive_manager):
    """Displays comprehensive attendance records and analytics from the database."""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="📋 Attendance Records & Analytics", 
                 font=("Segoe UI", 34, "bold"), text_color="#3b9dd8").pack(anchor="w")
    
    all_data = get_attendance_history()
    total_recs = len(all_data)
    present_recs = len([r for r in all_data if r['status'] == 'Present'])
    late_recs = len([r for r in all_data if r['status'] == 'Late'])
    absent_recs = len([r for r in all_data if r['status'] == 'Absent'])

    stats_row = ctk.CTkFrame(content_area, fg_color="transparent")
    stats_row.pack(fill="x", padx=30, pady=(0, 15))
    stats_row.columnconfigure((0, 1, 2, 3), weight=1)
    
    stats_data = [
        ("Total Records", str(total_recs), "#3498DB"),
        ("Present", str(present_recs), "#2ECC71"),
        ("Late", str(late_recs), "#F39C12"),
        ("Absent", str(absent_recs), "#E74C3C")
    ]
    
    for i, (label, value, color) in enumerate(stats_data):
        card = ctk.CTkFrame(stats_row, fg_color="#1a1a1a", corner_radius=10, height=80)
        card.grid(row=0, column=i, padx=5, sticky="nsew")
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color=color).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=label, font=("Arial", 11), text_color="gray").pack()
    
    filter_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    filter_bar.pack(fill="x", pady=(0, 15), padx=30)
    
    row1 = ctk.CTkFrame(filter_bar, fg_color="transparent")
    row1.pack(fill="x", padx=15, pady=15)
    
    search_entry = ctk.CTkEntry(row1, placeholder_text="🔍 Search Name/Reg No...", width=400, height=40, fg_color="#2c2c2c")
    search_entry.pack(side="left", padx=5)
    
    ctk.CTkButton(row1, text="📅 Reset Search", width=120, height=40, 
                 fg_color="#333333", command=lambda: search_entry.delete(0, 'end')).pack(side="left", padx=5)

    table_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=30, pady=(15, 30))
    
    header_box = ctk.CTkFrame(table_frame, fg_color="#0f0f0f", corner_radius=10)
    header_box.pack(fill="x", padx=20, pady=20)
    
    headers = ["Name", "Reg No", "Date", "Time In", "Time Out", "Status"]
    for h in headers:
        ctk.CTkLabel(header_box, text=h, font=("Arial", 13, "bold"), text_color="darkorange").pack(side="left", expand=True, padx=12, pady=15)
    
    scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
    scroll_table.pack(fill="both", expand=True, padx=5, pady=(0, 15))

    # Inner container to protect scrollbar internals
    scroll_container = ctk.CTkFrame(scroll_table, fg_color="transparent")
    scroll_container.pack(fill="both", expand=True)

    def update_table(query=""):
        for widget in scroll_container.winfo_children(): widget.destroy()
        filtered_list = all_data
        if query:
            query = query.lower()
            filtered_list = [r for r in all_data if query in r['name'].lower() or query in r['reg_no'].lower()]
        
        if not filtered_list:
            ctk.CTkLabel(scroll_container, text="No attendance records found.", font=("Arial", 14), text_color="gray").pack(pady=50)
            return

        for r in filtered_list:
            row = ctk.CTkFrame(scroll_container, fg_color="#2c2c2c", corner_radius=8)
            row.pack(fill="x", padx=20, pady=5)
            status_color = {"Present": "#2ECC71", "Late": "#F39C12", "Absent": "#E74C3C"}.get(r['status'], "gray")
            time_out = r['time_out'] if r['time_out'] else "---"
            ctk.CTkLabel(row, text=r['name'], font=("Arial", 12)).pack(side="left", expand=True, padx=12, pady=12)
            ctk.CTkLabel(row, text=r['reg_no'], font=("Arial", 12)).pack(side="left", expand=True, padx=12, pady=12)
            ctk.CTkLabel(row, text=str(r['date']), font=("Arial", 12)).pack(side="left", expand=True, padx=12, pady=12)
            ctk.CTkLabel(row, text=str(r['time_in']), font=("Arial", 12)).pack(side="left", expand=True, padx=12, pady=12)
            ctk.CTkLabel(row, text=str(time_out), font=("Arial", 12)).pack(side="left", expand=True, padx=12, pady=12)
            ctk.CTkLabel(row, text=r['status'], font=("Arial", 12, "bold"), text_color=status_color).pack(side="left", expand=True, padx=12, pady=12)

    update_table()
    search_entry.bind("<KeyRelease>", lambda e: update_table(search_entry.get()))

def show_present_list_content(content_area, responsive_manager):
    """Displays a list of students currently recognized in this session."""
    ctk.CTkLabel(content_area, text="✅ Recognized Students (Live)", font=("Segoe UI", 28, "bold"), text_color="#00c853").pack(anchor="w", padx=30, pady=(30, 10))
    summary_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    summary_bar.pack(fill="x", padx=30, pady=(0, 20))
    ctk.CTkLabel(summary_bar, text=f"Total Recognized: {len(present_details_list)}", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=20, pady=10)
    search_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    search_frame.pack(fill="x", padx=30, pady=(0, 10))
    ctk.CTkLabel(search_frame, text="🔍 Search Student:", font=("Arial", 12, "bold"), text_color="gray").pack(side="left")
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Type Name, Reg No...", width=350, height=35, corner_radius=10)
    search_entry.pack(side="left", padx=15)
    table_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    header = ctk.CTkFrame(table_frame, fg_color="#0f0f0f", corner_radius=10)
    header.pack(fill="x", padx=15, pady=15)
    cols = ["Name", "Reg No", "Course", "Program", "Date", "Time"]
    for text in cols:
        ctk.CTkLabel(header, text=text, font=("Arial", 12, "bold"), text_color="darkorange").pack(side="left", expand=True, fill="x")
    scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
    scroll_table.pack(fill="both", expand=True, padx=5, pady=(0, 15))

    # Inner container
    scroll_container = ctk.CTkFrame(scroll_table, fg_color="transparent")
    scroll_container.pack(fill="both", expand=True)

    def update_table(query=""):
        for widget in scroll_container.winfo_children(): widget.destroy()
        filtered_list = present_details_list
        if query:
            query = query.lower()
            filtered_list = [item for item in present_details_list if query in item['name'].lower() or query in item['reg'].lower()]
        if not filtered_list:
            ctk.CTkLabel(scroll_container, text="No matching students found.", font=("Arial", 14), text_color="gray").pack(pady=50)
            return
        for item in reversed(filtered_list):
            row = ctk.CTkFrame(scroll_container, fg_color="#2c2c2c", corner_radius=8)
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=item['name'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=item['reg'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=item['course'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=item['program'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=item['date'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=item['time'], font=("Arial", 11), text_color="#00c853").pack(side="left", expand=True, fill="x", pady=8)
    update_table()
    search_entry.bind("<KeyRelease>", lambda e: update_table(search_entry.get()))

def show_absent_list_content(content_area, responsive_manager):
    """Displays a list of students who have not been recognized today."""
    ctk.CTkLabel(content_area, text="❌ Students Absent (Live)", font=("Segoe UI", 28, "bold"), text_color="#9c27b0").pack(anchor="w", padx=30, pady=(30, 10))
    absent_students = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, reg_no, course, program, department FROM students")
            all_students = cursor.fetchall()
            absent_students = [s for s in all_students if s['reg_no'] not in present_student_ids]
            cursor.close()
            conn.close()
    except Exception as e: print(f"Error: {e}")
    summary_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    summary_bar.pack(fill="x", padx=30, pady=(0, 20))
    ctk.CTkLabel(summary_bar, text=f"Total Absent: {len(absent_students)}", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=20, pady=10)
    search_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    search_frame.pack(fill="x", padx=30, pady=(0, 10))
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Absent...", width=350, height=35, corner_radius=10)
    search_entry.pack(side="left", padx=15)
    table_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    header = ctk.CTkFrame(table_frame, fg_color="#0f0f0f", corner_radius=10)
    header.pack(fill="x", padx=15, pady=15)
    cols = ["Name", "Reg No", "Course", "Program", "Department"]
    for text in cols:
        ctk.CTkLabel(header, text=text, font=("Arial", 12, "bold"), text_color="darkorange").pack(side="left", expand=True, fill="x")
    scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
    scroll_table.pack(fill="both", expand=True, padx=5, pady=(0, 15))

    # Inner container
    scroll_container = ctk.CTkFrame(scroll_table, fg_color="transparent")
    scroll_container.pack(fill="both", expand=True)

    def update_table(query=""):
        for widget in scroll_container.winfo_children(): widget.destroy()
        query = query.lower()
        filtered_list = [s for s in absent_students if query in s['name'].lower() or query in s['reg_no'].lower()]
        for s in filtered_list:
            row = ctk.CTkFrame(scroll_container, fg_color="#2c2c2c", corner_radius=8)
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=s['name'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['reg_no'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['course'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['program'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['department'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
    update_table()
    search_entry.bind("<KeyRelease>", lambda e: update_table(search_entry.get()))

def show_all_students_list_content(content_area, responsive_manager):
    """Displays a list of all registered students in the system."""
    ctk.CTkLabel(content_area, text="👥 Registered Student Directory", font=("Segoe UI", 28, "bold"), text_color="darkorange").pack(anchor="w", padx=30, pady=(30, 10))
    all_students = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name, reg_no, course, program, department FROM students")
            all_students = cursor.fetchall()
            cursor.close()
            conn.close()
    except Exception as e: print(f"Error: {e}")
    summary_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    summary_bar.pack(fill="x", padx=30, pady=(0, 20))
    ctk.CTkLabel(summary_bar, text=f"Total Registered: {len(all_students)}", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=20, pady=10)
    search_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    search_frame.pack(fill="x", padx=30, pady=(0, 10))
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Students...", width=350, height=35, corner_radius=10)
    search_entry.pack(side="left", padx=15)
    table_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    header = ctk.CTkFrame(table_frame, fg_color="#0f0f0f", corner_radius=10)
    header.pack(fill="x", padx=15, pady=15)
    cols = ["Name", "Reg No", "Course", "Program", "Department"]
    for text in cols:
        ctk.CTkLabel(header, text=text, font=("Arial", 12, "bold"), text_color="white").pack(side="left", expand=True, fill="x")
    scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
    scroll_table.pack(fill="both", expand=True, padx=5, pady=(0, 15))

    # Inner container
    scroll_container = ctk.CTkFrame(scroll_table, fg_color="transparent")
    scroll_container.pack(fill="both", expand=True)

    def update_table(query=""):
        for widget in scroll_container.winfo_children(): widget.destroy()
        query = query.lower()
        filtered_list = [s for s in all_students if query in s['name'].lower() or query in s['reg_no'].lower()]
        for s in filtered_list:
            row = ctk.CTkFrame(scroll_container, fg_color="#2c2c2c", corner_radius=8)
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=s['name'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['reg_no'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['course'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['program'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
            ctk.CTkLabel(row, text=s['department'], font=("Arial", 11)).pack(side="left", expand=True, fill="x", pady=8)
    update_table()
    search_entry.bind("<KeyRelease>", lambda e: update_table(search_entry.get()))

def show_unknowns_list_content(content_area, responsive_manager, show_content_callback=None):
    """Displays a list of automatically captured unknown individuals."""
    ctk.CTkLabel(content_area, text="🕵️ Captured Unknowns", font=("Segoe UI", 28, "bold"), text_color="#ff5722").pack(anchor="w", padx=30, pady=(30, 10))
    base_dir = "unknowns"
    unknown_folders = []
    if os.path.exists(base_dir):
        folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        folders.sort(key=lambda x: os.path.getctime(os.path.join(base_dir, x)), reverse=True)
        for d in folders:
            folder_path = os.path.join(base_dir, d)
            img_count = len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            created_at = time.ctime(os.path.getctime(folder_path))
            unknown_folders.append({'id': d, 'count': img_count, 'time': created_at, 'path': folder_path})
    summary_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    summary_bar.pack(fill="x", padx=30, pady=(0, 20))
    ctk.CTkLabel(summary_bar, text=f"Total Unknown Sessions: {len(unknown_folders)}", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=20, pady=10)
    table_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    header = ctk.CTkFrame(table_frame, fg_color="#0f0f0f", corner_radius=10)
    header.pack(fill="x", padx=15, pady=15)
    cols = ["Capture ID", "Images Captured", "Time Detected", "Action"]
    for text in cols:
        ctk.CTkLabel(header, text=text, font=("Arial", 12, "bold"), text_color="white").pack(side="left", expand=True, fill="x")
    scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
    scroll_table.pack(fill="both", expand=True, padx=5, pady=(0, 15))
    for session in unknown_folders:
        row = ctk.CTkFrame(scroll_table, fg_color="#2c2c2c", corner_radius=8)
        row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row, text=session['id'], text_color="#ff5722", font=("Arial", 12, "bold")).pack(side="left", expand=True, fill="x", pady=10)
        ctk.CTkLabel(row, text=f"{session['count']} frames").pack(side="left", expand=True, fill="x", pady=10)
        ctk.CTkLabel(row, text=session['time']).pack(side="left", expand=True, fill="x", pady=10)
        def view_images(p=session['path'], sid=session['id']):
            if show_content_callback:
                show_content_callback(lambda a, r: show_unknown_session_images(a, r, sid, p, show_content_callback=show_content_callback))
        ctk.CTkButton(row, text="🖼️ View Images", command=view_images, fg_color="#ff5722", hover_color="#e64a19", height=28, width=100).pack(side="right", padx=10)

def show_unknown_session_images(area, rm, session_id, folder_path, show_content_callback=None):
    """Gallery of images for an unknown session."""
    header = ctk.CTkFrame(area, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(30, 10))
    ctk.CTkButton(header, text="← Back", command=lambda: show_content_callback(lambda a, r: show_unknowns_list_content(a, r, show_content_callback=show_content_callback)) if show_content_callback else None).pack(side="left")
    ctk.CTkLabel(header, text=f"📂 Session: {session_id}", font=("Segoe UI", 24, "bold"), text_color="#ff5722").pack(side="left", padx=20)
    scroll = ctk.CTkScrollableFrame(area, fg_color="#1a1a1a", corner_radius=15)
    scroll.pack(fill="both", expand=True, padx=30, pady=10)
    if os.path.exists(folder_path):
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        images.sort()
        for img_name in images:
            try:
                pil_img = Image.open(os.path.join(folder_path, img_name))
                pil_img.thumbnail((200, 200))
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(180, 150))
                ctk.CTkLabel(scroll, text="", image=ctk_img).pack(side="left", padx=10, pady=10)
            except: pass
