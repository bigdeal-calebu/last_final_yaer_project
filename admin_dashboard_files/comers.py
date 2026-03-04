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
    
    # Mock Data
    mock_data = [
        ("Alice Wonder", "REG-001", "07:45 AM", "Computer Science", "Early"),
        ("Bob Builder", "REG-002", "07:50 AM", "Engineering", "Early"),
        ("Charlie Chap", "REG-003", "07:55 AM", "Mathematics", "Early"),
    ]
    
    for name, reg, time, course, status in mock_data:
        row = ctk.CTkFrame(table_scroll, fg_color="#2c2c2c", corner_radius=5, height=40)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        ctk.CTkLabel(row, text=name).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=reg).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=time).pack(side="left", expand=True)
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
    
    # Mock Data
    mock_data = [
        ("Dave Diver", "REG-055", "08:15 AM", "Biology", "Late"),
        ("Eve Adams", "REG-067", "08:20 AM", "Physics", "Late"),
    ]
    
    for name, reg, time, course, status in mock_data:
        row = ctk.CTkFrame(table_scroll, fg_color="#2c2c2c", corner_radius=5, height=40)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        ctk.CTkLabel(row, text=name).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=reg).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=time).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=course).pack(side="left", expand=True)
        ctk.CTkLabel(row, text=status, text_color="#E74C3C").pack(side="left", expand=True)
