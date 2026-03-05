import customtkinter as ctk

def show_early_comers_content(content_area, responsive_manager):
    """View students who arrived early"""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="🌅 Early Comers", 
                 font=("Segoe UI", 32, "bold"), text_color="#2ECC71").pack(anchor="w")
    
    # Filter
    filter_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    filter_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    ctk.CTkLabel(filter_frame, text="Filter by Date:", font=("Arial", 12)).pack(side="left", padx=20, pady=15)
    ctk.CTkButton(filter_frame, text="Today", width=100, fg_color="#333333").pack(side="left", padx=5)
    ctk.CTkButton(filter_frame, text="This Week", width=100, fg_color="#333333").pack(side="left", padx=5)
    ctk.CTkButton(filter_frame, text="Custom Range", width=120, fg_color="#2ECC71", text_color="black").pack(side="left", padx=15)

    # Table
    table_container = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_container.pack(fill="both", expand=True, padx=30, pady=10)
    
    # Headers
    headers = ["Name", "Reg No", "Arrival Time", "Course", "Status"]
    header_row = ctk.CTkFrame(table_container, fg_color="#333333", corner_radius=10, height=50)
    header_row.pack(fill="x", padx=10, pady=10)
    header_row.pack_propagate(False)
    
    for h in headers:
        ctk.CTkLabel(header_row, text=h, font=("Arial", 12, "bold"), text_color="white").pack(side="left", expand=True)

    table_scroll = ctk.CTkFrame(table_container, fg_color="transparent")
    table_scroll.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Fetch Real Data and Apply Configured Time Rule
    from db import get_attendance_history
    import admin_dashboard_files.config_manager as config_manager
    from datetime import datetime
    
    threshold_str = config_manager.get("late_arrival_time") # "08:30:00"
    try:
        threshold_time = datetime.strptime(threshold_str, "%H:%M:%S").time()
    except:
        threshold_time = datetime.strptime("08:30:00", "%H:%M:%S").time()
        
    all_attendance = get_attendance_history()
    early_comers = []
    
    for row in all_attendance:
        # Assuming database time_in is a timedelta or string
        t_str = str(row['time_in'])
        try:
            arrival_time = datetime.strptime(t_str, "%H:%M:%S").time()
            if arrival_time <= threshold_time:
                early_comers.append((
                    row['name'],
                    row['reg_no'], 
                    arrival_time.strftime("%I:%M %p"),
                    row['course'],
                    "Early"
                ))
        except: pass
    
    for name, reg, time_str, course, status in early_comers:
        row = ctk.CTkFrame(table_scroll, fg_color="#2c2c2c", corner_radius=5, height=40)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        ctk.CTkLabel(row, text=name).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=reg).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=time_str).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=course).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=status, text_color="#2ECC71").pack(side="left", expand=True)

def show_late_comers_content(content_area, responsive_manager):
    """View students who arrived late"""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="🏃 Late Comers", 
                 font=("Segoe UI", 32, "bold"), text_color="#E74C3C").pack(anchor="w")
    
    # Filter
    filter_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    filter_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    ctk.CTkLabel(filter_frame, text="Filter by Date:", font=("Arial", 12)).pack(side="left", padx=20, pady=15)
    ctk.CTkButton(filter_frame, text="Today", width=100, fg_color="#333333").pack(side="left", padx=5)
    ctk.CTkButton(filter_frame, text="This Week", width=100, fg_color="#333333").pack(side="left", padx=5)

    # Table
    table_container = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12)
    table_container.pack(fill="both", expand=True, padx=30, pady=10)
    
    # Headers
    headers = ["Name", "Reg No", "Arrival Time", "Course", "Status"]
    header_row = ctk.CTkFrame(table_container, fg_color="#333333", corner_radius=10, height=50)
    header_row.pack(fill="x", padx=10, pady=10)
    header_row.pack_propagate(False)
    
    for h in headers:
        ctk.CTkLabel(header_row, text=h, font=("Arial", 12, "bold"), text_color="white").pack(side="left", expand=True)

    table_scroll = ctk.CTkFrame(table_container, fg_color="transparent")
    table_scroll.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Fetch Real Data and Apply Configured Time Rule
    from db import get_attendance_history
    import admin_dashboard_files.config_manager as config_manager
    from datetime import datetime
    
    threshold_str = config_manager.get("late_arrival_time")
    try:
        threshold_time = datetime.strptime(threshold_str, "%H:%M:%S").time()
    except:
        threshold_time = datetime.strptime("08:30:00", "%H:%M:%S").time()
        
    all_attendance = get_attendance_history()
    late_comers = []
    
    for row in all_attendance:
        t_str = str(row['time_in'])
        try:
            arrival_time = datetime.strptime(t_str, "%H:%M:%S").time()
            if arrival_time > threshold_time:
                late_comers.append((
                    row['name'],
                    row['reg_no'], 
                    arrival_time.strftime("%I:%M %p"),
                    row['course'],
                    "Late"
                ))
        except: pass
    
    for name, reg, time_str, course, status in late_comers:
        row = ctk.CTkFrame(table_scroll, fg_color="#2c2c2c", corner_radius=5, height=40)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        ctk.CTkLabel(row, text=name).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=reg).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=time_str).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=course).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=status, text_color="#E74C3C").pack(side="left", expand=True)
