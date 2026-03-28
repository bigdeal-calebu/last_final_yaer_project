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
    # ── 1. CLEANUP ──────────────────────────────────────────────────
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ── 2. BASE CONTAINERS ──────────────────────────────────────────
    # Top Header
    app_header = header.create_header(parent_frame, title_text="ADMIN PORTAL", subtitle_text="System Management")
    
    # Navigation Ribbon (Mobile/Tablet)
    ribbon_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
    
    # Content Area
    body_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    body_frame.pack(fill="both", expand=True)

    sidebar = ctk.CTkScrollableFrame(body_frame, fg_color="#101214", corner_radius=0, width=220)
    content_area = ctk.CTkScrollableFrame(body_frame, fg_color="#151515", corner_radius=0)

    # Actual Page Content (Inside Scrollable Content Area)
    main_page_container = ctk.CTkFrame(content_area, fg_color="transparent")
    main_page_container.pack(fill="both", expand=True)

    # ── 3. RESPONSIVE MANAGER ───────────────────────────────────────
    rm = layout.ResponsiveManager(body_frame, sidebar, content_area, has_sidebar=True)
    rm.create_hamburger_button(app_header.controls_frame)

    # Track current page for auto-refresh
    _current_renderer = [None]
    def _rerender():
        if _current_renderer[0]:
            _current_renderer[0]()

    # Profile info in Header
    def show_header_profile():
        for w in app_header.controls_frame.winfo_children():
            # Preserving Hamburg, Refresh and Theme buttons
            if w == rm.hamburger_btn: continue
            if isinstance(w, ctk.CTkButton) and w.cget("text") in ("🔄", "☀️", "🌙"):
                continue
            w.destroy()
        
        if not admin_data: return
        
        container = ctk.CTkFrame(app_header.controls_frame, fg_color="#1a1c1e", corner_radius=20)
        container.pack(side="right", padx=10)
        
        p = admin_data.get('photo_path')
        if p and os.path.exists(p):
            try:
                img = ctk.CTkImage(Image.open(p), size=(32, 32))
                ctk.CTkLabel(container, image=img, text="").pack(side="left", padx=5, pady=5)
            except: ctk.CTkLabel(container, text="👤").pack(side="left", padx=8)
        else: ctk.CTkLabel(container, text="👤").pack(side="left", padx=8)
        
        ctk.CTkLabel(container, text=admin_data.get('name','Admin'), font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

    show_header_profile()

    # ── 4. CONTENT LOADER ───────────────────────────────────────────
    def show_content(page_func):
        rm.hide_sidebar()
        shared.release_camera_stream()
        rm.registered_grids = []
        for w in main_page_container.winfo_children():
            w.destroy()
        
        def render():
            page_func(main_page_container, rm)
        
        _current_renderer[0] = render
        render()

    # ── 5. MENU BUILDERS ────────────────────────────────────────────
    menu_data = [
        ("🏠 Home", lambda: lambda area, rm: home.show_home_content(area, rm, admin_data, show_content_callback=show_content)),
        ("📸 Dataset", lambda: generate_dataset.show_generate_dataset_content),
        ("🧠 Training", lambda: train_classifier.show_train_classifier_content),
        ("🔍 Recognition", lambda: face_recognition.show_face_recognition_content),
        ("📊 Records", lambda: view_attendance.show_attendance_history_content),
        ("➕ Register", lambda: admin_register_student.show_register_student_content),
        ("🔄 Update", lambda: update_users.show_update_users_content),
        ("📢 Notify", lambda: lambda area, rm: announcements.show_announcement_content(area, rm, admin_data)),
        ("⚙️ Settings", lambda: settings.show_settings_content),
    ]

    def _build_sidebar():
        for w in sidebar.winfo_children(): w.destroy()
        ctk.CTkLabel(sidebar, text="MANAGEMENT", font=("Arial", 11, "bold"), text_color="#555").pack(pady=(20, 10), padx=20, anchor="w")
        
        for label, func_getter in menu_data:
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", fg_color="darkorange", text_color="black",
                hover_color="#e67e22", height=38, font=("Arial", 13, "bold"),
                command=lambda f=func_getter(): show_content(f)
            )
            btn.pack(fill="x", padx=15, pady=2)
        
        ctk.CTkButton(
            sidebar, text="🚪 Logout", anchor="w", fg_color="#E74C3C", text_color="white",
            hover_color="#c0392b", height=38, font=("Arial", 13, "bold"),
            command=on_logout_click
        ).pack(fill="x", padx=15, pady=(20, 10))

    def _build_ribbon(cols=4):
        for w in ribbon_container.winfo_children(): w.destroy()
        grid = ctk.CTkFrame(ribbon_container, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=5)
        
        for i, (label, func_getter) in enumerate(menu_data):
            btn = ctk.CTkButton(
                grid, text=label, fg_color="#222", text_color="white",
                hover_color="darkorange", height=32, font=("Arial", 11, "bold"),
                command=lambda f=func_getter(): show_content(f)
            )
            btn.grid(row=i//cols, column=i%cols, padx=3, pady=3, sticky="ew")
        for c in range(cols): grid.columnconfigure(c, weight=1)

    # ── 6. MODE CALLBACKS ───────────────────────────────────────────
    def on_mode_change():
        mode = rm.mode
        if mode == "desktop":
            ribbon_container.pack_forget()
            rm.has_sidebar = True
            rm._apply_desktop()
            _build_sidebar()
            if rm.hamburger_btn: rm.hamburger_btn.pack_forget()
        elif mode == "tiny":
            rm.has_sidebar = False
            rm._apply_small()
            ribbon_container.pack_forget()
            if rm.hamburger_btn: rm.hamburger_btn.pack(side="right", padx=8)
        else: # Mobile / Tablet
            rm.has_sidebar = False
            rm._apply_small()
            cols = 3 if mode == "mobile" else 5
            _build_ribbon(cols)
            ribbon_container.pack(fill="x", pady=(0, 2), before=body_frame)
            if rm.hamburger_btn: rm.hamburger_btn.pack_forget()
        
        _rerender()

    rm.on_mode_change = on_mode_change
    rm.on_any_resize = lambda w: _rerender()

    # Initial Load
    show_content(lambda area, rm: home.show_home_content(area, rm, admin_data, show_content_callback=show_content))
    on_mode_change()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ctk.CTk()
    app.title("Modern Dashboard")
    app.geometry("1100x700")
    create_admin_dashboard(app, app.destroy, admin_data={"name": "Admin User"})
    app.mainloop()
