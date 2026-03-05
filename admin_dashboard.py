import customtkinter as ctk
import os
import layout
from PIL import Image
import header
from admin_dashboard_files import (
    shared, home, generate_dataset, train_classifier, 
    face_recognition, view_attendance, admin_register_student, 
    update_users, upload_images, comers, 
    settings, announcements, export_and_help, add_admin
)

def create_admin_dashboard(parent_frame, on_logout_click, admin_data=None):
    # Clear existing widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    layout.setup_dashboard_layout(parent_frame)
    
    # 1. Main Header
    app_header = header.create_header(parent_frame, title_text="Smart Attendance Dashboard", subtitle_text="Admin Overview")
    
    # Profile in Header
    if admin_data:
        admin_name = admin_data.get('name', 'Admin')
        photo_path = admin_data.get('photo_path')        
        profile_container = ctk.CTkFrame(app_header.controls_frame, fg_color="#1a1a1a", corner_radius=20)
        profile_container.pack(side="left", padx=10)
        
        if photo_path and os.path.exists(photo_path):
            try:
                admin_img = ctk.CTkImage(light_image=Image.open(photo_path), dark_image=Image.open(photo_path), size=(35, 35))
                ctk.CTkLabel(profile_container, image=admin_img, text="", corner_radius=20).pack(side="left", padx=5, pady=5)
            except:
                ctk.CTkLabel(profile_container, text="👤", font=("Arial", 20)).pack(side="left", padx=5, pady=5)
        else:
            ctk.CTkLabel(profile_container, text="👤", font=("Arial", 20)).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(profile_container, text=admin_name, font=("Arial", 12, "bold"), text_color="white").pack(side="left", padx=(0, 10), pady=5)

    # 2. Body Frame (Sidebar + Content)
    body_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    body_frame.pack(fill="both", expand=True)
    body_frame.columnconfigure(0, weight=0, minsize=240)
    body_frame.columnconfigure(1, weight=1)
    body_frame.rowconfigure(0, weight=1)

    sidebar = ctk.CTkScrollableFrame(body_frame, fg_color="#151515", corner_radius=0, width=240, scrollbar_button_color="darkorange")
    sidebar.grid(row=0, column=0, sticky="nsew")
    ctk.CTkLabel(sidebar, text="ADMIN MENU", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(20,10), padx=20, anchor="w")
    
    content_area = ctk.CTkScrollableFrame(body_frame, fg_color="#2b2b2b", corner_radius=0, scrollbar_button_color="#3b9dd8")
    content_area.grid(row=0, column=1, sticky="nsew")

    # Inner container for page content (to avoid destroying scrollbar internals)
    main_page_container = ctk.CTkFrame(content_area, fg_color="transparent")
    main_page_container.pack(fill="both", expand=True)

    responsive_manager = layout.ResponsiveManager(parent_frame, sidebar, content_area)

    def show_content(new_page_function):
        shared.release_camera_stream()
        responsive_manager.registered_grids = []
        for widget in main_page_container.winfo_children():
            widget.destroy()            
        content_area.after(10, lambda: new_page_function(main_page_container, responsive_manager))
    

    # Menu Structure
    menu_data = {
        "CORE": [
            ("🏠 Home", lambda: show_content(lambda area, rm: home.show_home_content(area, rm, admin_data, show_content_callback=show_content))),
            ("📸 Generate Dataset", lambda: show_content(generate_dataset.show_generate_dataset_content)),
            ("🧠 Train Classifier", lambda: show_content(train_classifier.show_train_classifier_content)),
            ("🔍 Face Recognition", lambda: show_content(face_recognition.show_face_recognition_content)),
            ("📋 View Attendance", lambda: show_content(view_attendance.show_attendance_content)),
        ],
        "STUDENTS": [
            ("➕ Register Student", lambda: show_content(lambda area, rm: admin_register_student.show_register_student_content(area, rm))),
            ("🔄 Update Users", lambda: show_content(update_users.show_update_users_content)),
        ],
        "MANAGEMENT": [
            ("👤 Add Admin", lambda: show_content(add_admin.show_add_admin_content)),
        ],
        "REPORTS": [
            ("🌅 Early Comers", lambda: show_content(comers.show_early_comers_content)),
            ("🌇 Late Comers", lambda: show_content(comers.show_late_comers_content)),
            ("📥 Export Attendance", lambda: show_content(export_and_help.show_export_content)),
        ],
        "SYSTEM": [
            ("📢 Announcement", lambda: show_content(lambda area, rm: announcements.show_announcement_content(area, rm, admin_data))),
            ("⚙️ Settings", lambda: show_content(settings.show_settings_content)),
            ("❓ Help", lambda: show_content(export_and_help.show_help_content)),
        ]
    }

    # Render Sidebar Buttons
    for section_name, items in menu_data.items():
        ctk.CTkLabel(sidebar, text=section_name, font=("Arial", 11, "bold"), text_color="#555555").pack(pady=(15, 5), padx=25, anchor="w")
        for label, cmd in items:
            btn = ctk.CTkButton(sidebar, text=label, anchor="w", fg_color="darkorange", text_color="black", hover_color="#e67e22", height=40, font=("Arial", 13, "bold"), command=cmd)
            btn.pack(fill="x", padx=15, pady=2)

    ctk.CTkLabel(sidebar, text="ACCOUNT", font=("Arial", 11, "bold"), text_color="#555555").pack(pady=(15, 5), padx=25, anchor="w")
    ctk.CTkButton(sidebar, text="🚪 Logout", anchor="w", fg_color="#E74C3C", text_color="white", hover_color="#c0392b", height=40, font=("Arial", 13, "bold"), command=on_logout_click).pack(fill="x", padx=15, pady=2)

    # Load Home by default
    show_content(lambda area, rm: home.show_home_content(area, rm, admin_data, show_content_callback=show_content))

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ctk.CTk()
    app.title("Modern Dashboard")
    app.geometry("1100x700")
    create_admin_dashboard(app, app.destroy, admin_data={"name": "Admin User"})
    app.mainloop()
