import customtkinter as ctk
from tkinter import messagebox

def show_export_content(content_area, responsive_manager):
    """Export System Data"""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="📥 Export Data", 
                 font=("Segoe UI", 32, "bold"), text_color="#3498DB").pack(anchor="w")

    export_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    export_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    # Export Options
    ctk.CTkLabel(export_frame, text="Select Data to Export:", font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=30, pady=(30, 20))
    
    options = ["Attendance Records", "Student Profiles", "System Logs", "User Activity"]
    for opt in options:
        ctk.CTkCheckBox(export_frame, text=opt, font=("Arial", 14)).pack(anchor="w", padx=50, pady=10)
    
    ctk.CTkLabel(export_frame, text="Select Format:", font=("Arial", 16, "bold"), text_color="white").pack(anchor="w", padx=30, pady=(30, 20))
    
    format_seg = ctk.CTkSegmentedButton(export_frame, values=["CSV", "Excel", "PDF", "JSON"])
    format_seg.pack(anchor="w", padx=50, pady=10)
    format_seg.set("Excel")
    
    # Export Button
    def handle_export():
        messagebox.showinfo("Export", "Data export started! File will be saved to Downloads.")
        
    ctk.CTkButton(export_frame, text="START EXPORT", height=50, width=200, 
                 font=("Arial", 14, "bold"), fg_color="#3498DB", command=handle_export).pack(pady=50)

def show_help_content(content_area, responsive_manager):
    """Comprehensive Help & Documentation Center."""
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="❓ HELP & DOCUMENTATION CENTER", 
                 font=("Segoe UI", 32, "bold"), text_color="#3b9dd8").pack(anchor="w")
    
    ctk.CTkLabel(header_frame, text="Find answers, guides, and support for the Student Attendance System", 
                 font=("Arial", 12), text_color="gray").pack(anchor="w", pady=(5, 0))
    
    # Search Bar
    search_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=12, height=70)
    search_frame.pack(fill="x", padx=30, pady=(10, 20))
    
    search_inner = ctk.CTkFrame(search_frame, fg_color="transparent")
    search_inner.pack(fill="x", padx=20, pady=15)
    
    search_entry = ctk.CTkEntry(search_inner, placeholder_text="🔍 Search documentation...", 
                                height=40, font=("Arial", 13), fg_color="#2c2c2c", 
                                border_color="#3b9dd8", width=500)
    search_entry.pack(side="left", padx=(0, 10))
    
    ctk.CTkButton(search_inner, text="SEARCH", fg_color="#3b9dd8", 
                  width=120, height=40, font=("Arial", 12, "bold")).pack(side="left")
    
    help_scroll = ctk.CTkFrame(content_area, fg_color="transparent")
    help_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    # SECTION 1: QUICK START GUIDES
    quick_start_header = ctk.CTkFrame(help_scroll, fg_color="#2ECC71", corner_radius=10, height=45)
    quick_start_header.pack(fill="x", pady=(10, 15))
    ctk.CTkLabel(quick_start_header, text="🚀 QUICK START GUIDES", 
                 font=("Arial", 16, "bold"), text_color="white").pack(pady=10)
    
    quick_guides = [
        ("📝 Register a New Student", "Step-by-step guide to add students to the system", "#2ECC71"),
        ("📸 Upload Biometric Photos", "How to capture and upload student face images", "#3498DB"),
        ("📊 View Attendance Reports", "Generate and export attendance data", "#F39C12"),
        ("⚙️ Configure System Settings", "Customize system preferences and security", "#9B59B6")
    ]
    
    for title, description, color in quick_guides:
        guide_card = ctk.CTkFrame(help_scroll, fg_color="#1a1a1a", corner_radius=10, 
                                 border_width=2, border_color=color)
        guide_card.pack(fill="x", pady=8)
        content_frame = ctk.CTkFrame(guide_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info_frame, text=title, text_color=color, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=description, text_color="gray", font=("Arial", 11)).pack(anchor="w", pady=(3, 0))
        ctk.CTkButton(content_frame, text="View Guide →", fg_color=color, width=130, height=35, font=("Arial", 11, "bold")).pack(side="right")
    
    # SECTION 2: FEATURE DOCUMENTATION
    features_header = ctk.CTkFrame(help_scroll, fg_color="#3498DB", corner_radius=10, height=45)
    features_header.pack(fill="x", pady=(25, 15))
    ctk.CTkLabel(features_header, text="📚 FEATURE DOCUMENTATION", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)
    
    features = [
        ("👥 Student Management", "Register, update, and manage student records and profiles"),
        ("📷 Face Recognition System", "AI-powered biometric attendance tracking"),
        ("📊 Attendance Analytics", "View detailed reports, statistics, and trends"),
        ("🔐 Admin Controls", "User management, permissions, and security settings"),
        ("📥 Data Export", "Export data in CSV, Excel, PDF, and JSON formats"),
        ("📢 Announcements", "Create and manage system-wide notifications"),
        ("🗄️ Database Management", "Backup, restore, and optimize database"),
        ("🔧 System Maintenance", "Logs, cache management, and troubleshooting")
    ]
    
    for title, description in features:
        feature_row = ctk.CTkFrame(help_scroll, fg_color="#2c2c2c", corner_radius=8)
        feature_row.pack(fill="x", pady=6)
        row_content = ctk.CTkFrame(feature_row, fg_color="transparent")
        row_content.pack(fill="x", padx=20, pady=12)
        info = ctk.CTkFrame(row_content, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info, text=title, text_color="darkorange", font=("Arial", 13, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=description, text_color="gray", font=("Arial", 10)).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(row_content, text="Read More", fg_color="#3498DB", width=110, height=30, font=("Arial", 10, "bold")).pack(side="right")

    # FAQ
    faq_header = ctk.CTkFrame(help_scroll, fg_color="#F39C12", corner_radius=10, height=45)
    faq_header.pack(fill="x", pady=(25, 15))
    ctk.CTkLabel(faq_header, text="💬 FREQUENTLY ASKED QUESTIONS", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)
    
    faqs = [
        ("How do I reset my admin password?", "Contact the system administrator or use the 'Forgot Password' option on the login page."),
        ("Can I export attendance data for a specific date range?", "Yes, use the Export feature and select your desired date range using the date picker."),
    ]
    
    for question, answer in faqs:
        faq_card = ctk.CTkFrame(help_scroll, fg_color="#2c2c2c", corner_radius=8)
        faq_card.pack(fill="x", pady=6)
        faq_content = ctk.CTkFrame(faq_card, fg_color="transparent")
        faq_content.pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(faq_content, text=f"Q: {question}", text_color="#F39C12", font=("Arial", 12, "bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(faq_content, text=f"A: {answer}", text_color="lightgray", font=("Arial", 11), anchor="w").pack(anchor="w", pady=(5, 0))
