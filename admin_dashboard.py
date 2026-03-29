import customtkinter as ctk
import os
import layout
from PIL import Image
import header
from admin_dashboard_files import (
    shared, home, generate_dataset, train_classifier, 
    face_recognition, view_attendance, admin_register_student, 
    update_users, settings, announcements, 
    export_and_help, add_admin, prediction
)

from db import get_all_archives


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
    # Use the dedicated menu_holder for the hamburger to ensure it's never obscured
    rm.create_hamburger_button(app_header.menu_holder)


    # Track current page for auto-refresh
    _current_renderer = [None]
    _current_mode = [None]
    
    def _rerender(force=False):
        if not force and rm.mode == _current_mode[0]:
            return # Skip if layout mode hasn't changed
        
        _current_mode[0] = rm.mode
        if _current_renderer[0]:
            _current_renderer[0]()


    # Profile info in Header
    def show_header_profile():
        for w in app_header.controls_frame.winfo_children():
            if isinstance(w, ctk.CTkButton) and w.cget("text") in ("🔄", "☀️", "🌙"):
                continue
            w.destroy()
        
        # Ensure the hamburger in the separate menu_holder is always visible on small screens
        if rm.hamburger_btn:
            rm.hamburger_btn.pack(side="right", padx=10, pady=5)

        
        if not admin_data: return
        
        is_small = rm.is_small()
        container_pad = 5 if is_small else 10
        container = ctk.CTkFrame(app_header.controls_frame, fg_color="#1a1c1e", corner_radius=15 if is_small else 20)
        container.pack(side="right", padx=container_pad)

        
        p = admin_data.get('photo_path')
        if p and os.path.exists(p):
            try:
                img = ctk.CTkImage(Image.open(p), size=(32, 32))
                ctk.CTkLabel(container, image=img, text="").pack(side="left", padx=5, pady=5)
            except: ctk.CTkLabel(container, text="👤").pack(side="left", padx=8)
        else: ctk.CTkLabel(container, text="👤").pack(side="left", padx=8)
        
        name_font = ("Arial", 11 if is_small else 12, "bold")
        ctk.CTkLabel(container, text=admin_data.get('name','Admin'), font=name_font).pack(side="left", padx=(0, container_pad))


    show_header_profile()

    # ── 4. CONTENT LOADER (ASYNC SUPPORT) ───────────────────────────
    _loading_label_ref = [None]
    
    def get_loading_label():
        if _loading_label_ref[0] is None or not _loading_label_ref[0].winfo_exists():
            _loading_label_ref[0] = ctk.CTkLabel(main_page_container, text="⌛ Loading...", font=("Arial", 24, "bold"), text_color="gray")
        return _loading_label_ref[0]


    def show_content(page_func, data_loader=None):
        """
        Switches pages. If data_loader is provided, it runs in background
        before calling page_func with the loaded data.
        """
        rm.hide_sidebar()
        shared.release_camera_stream()
        rm.registered_grids = []
        
        # Clear current view (except the persistent loading label)
        lbl = get_loading_label()
        for w in main_page_container.winfo_children():
            if w != lbl:
                w.destroy()
        
        if data_loader:
            lbl.pack(expand=True, pady=100)
            
            def on_data_ready(data):
                def final_render():
                    if not main_page_container.winfo_exists():
                        return
                    
                    curr_lbl = get_loading_label()
                    curr_lbl.pack_forget()

                    for w in main_page_container.winfo_children():
                        if w != curr_lbl: 
                            try: w.destroy()
                            except: pass
                    
                    def render():
                        # Support functions that take data or just (area, rm)
                        try: page_func(main_page_container, rm, data)
                        except TypeError: page_func(main_page_container, rm)

                    
                    _current_renderer[0] = render
                    render()
                
                # Use after() to ensure UI update happens on main thread
                parent_frame.after(0, final_render)
            
            shared.run_in_background(data_loader, on_data_ready)
        else:
            def render():
                page_func(main_page_container, rm)
            
            _current_renderer[0] = render
            render()


    # ── 5. MENU BUILDERS ────────────────────────────────────────────
    # Cache last sync time to avoid redundant expensive Excel generations
    _last_sync_time = [0] 

    def get_archives_with_sync():
        """Returns the current archives and kicks off a refresh in the background."""
        import time
        from admin_dashboard_files.attendance_archiver import sync_live_excel
        from datetime import datetime, timedelta
        from db import get_all_archives
        
        now = time.time()
        # Launch sync in background if more than 30s since last
        if now - _last_sync_time[0] > 30:
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Start the heavy sync task in a ghost thread
            def do_background_sync():
                sync_live_excel(today)
                sync_live_excel(yesterday)
            
            shared.run_in_background(do_background_sync)
            _last_sync_time[0] = now
        
        # ALWAYS return what we currently have in DB immediately for zero friction
        return get_all_archives()

    menu_data = [

        ("🏠 Home", lambda: lambda area, rm: home.show_home_content(area, rm, admin_data, show_content_callback=show_content)),
        ("📸 Dataset", lambda: generate_dataset.show_generate_dataset_content),
        ("🧠 Training", lambda: train_classifier.show_train_classifier_content),
        ("🔍 Recognition", lambda: face_recognition.show_face_recognition_content),
        ("🧠 Prediction", lambda: prediction.show_prediction_content),
        ("📊 Records", lambda: (view_attendance.show_attendance_history_content, get_archives_with_sync)),
        ("➕ Register", lambda: admin_register_student.show_register_student_content),

        ("🔄 Update", lambda: update_users.show_update_users_content),
        ("📢 Notify", lambda: (lambda area, rm: announcements.show_announcement_content(area, rm, admin_data))),
        ("⚙️ Settings", lambda: settings.show_settings_content),
        ("🛠 Support", lambda: export_and_help.show_help_content),
        ("👤 Add Admin", lambda: add_admin.show_add_admin_content),
    ]





    def _build_sidebar():
        for w in sidebar.winfo_children(): w.destroy()
        ctk.CTkLabel(sidebar, text="MANAGEMENT", font=("Arial", 11, "bold"), text_color="#555").pack(pady=(20, 10), padx=20, anchor="w")
        
        for label, getter in menu_data:
            # getter() now returns (func, loader) or just func
            res = getter()
            page_func, loader = res if isinstance(res, tuple) else (res, None)
            
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", fg_color="darkorange", text_color="black",
                hover_color="#e67e22", height=38, font=("Arial", 13, "bold"),
                command=lambda f=page_func, l=loader: show_content(f, l)
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
        
        for i, (label, getter) in enumerate(menu_data):
            res = getter()
            page_func, loader = res if isinstance(res, tuple) else (res, None)
            
            btn = ctk.CTkButton(
                grid, text=label, fg_color="#222", text_color="white",
                hover_color="darkorange", height=32, font=("Arial", 11, "bold"),
                command=lambda f=page_func, l=loader: show_content(f, l)
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
        else: # Small devices (Tiny / Mobile / Tablet)
            rm.has_sidebar = False
            rm._apply_small()
            ribbon_container.pack_forget()
            # Ensure sidebar is built
            _build_sidebar()
            if rm.hamburger_btn: 
                # Re-pack it into its dedicated menu_holder
                rm.hamburger_btn.pack_forget()
                rm.hamburger_btn.pack(side="right", padx=10, pady=5)




        
        _rerender()

    rm.on_mode_change = on_mode_change
    rm.on_any_resize = lambda w: _rerender(force=False)


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
