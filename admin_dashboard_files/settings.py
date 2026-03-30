import customtkinter as ctk
from tkinter import messagebox




def show_settings_content(content_area, responsive_manager):
    """ Comprehensive system settings and configuration interface. """
    import admin_dashboard_files.config_manager as config_manager
    import modify_live
    
    is_small = responsive_manager.is_small()
    side_pad = 10 if is_small else 30
    wrap_len = 280 if is_small else 800

    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=side_pad, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="⚙️ SYSTEM SETTINGS", 
                 font=("Segoe UI", 24 if is_small else 32, "bold"), text_color="#3b9dd8",
                 wraplength=wrap_len).pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Configure core application behavior. Changes apply instantly.", 
                 font=("Segoe UI", 11 if is_small else 12), text_color="gray",
                 wraplength=wrap_len).pack(anchor="w", pady=(0, 20))

                 
    # Use a solid transparent frame to avoid nested scrollbars
    settings_scroll = ctk.CTkFrame(content_area, fg_color="transparent")
    settings_scroll.pack(fill="both", expand=True, padx=side_pad, pady=(10, 20))


    
    # --- 1. Camera Settings ---
    cam_section = ctk.CTkFrame(settings_scroll, fg_color="#3498DB", corner_radius=10, height=45)
    cam_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(cam_section, text="🎥 CAMERA & PERFORMANCE", font=("Arial", 12 if is_small else 14, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(pady=10)

    
    cam_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    cam_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(cam_container, text="Active Camera Index", font=("Arial", 12, "bold"), text_color="gray", wraplength=wrap_len).pack(anchor="w", padx=20, pady=(10,0))
    camera_idx_var = ctk.StringVar(value=str(config_manager.get("camera_index")))
    ctk.CTkOptionMenu(cam_container, variable=camera_idx_var, values=["0", "1", "2"], width=150, fg_color="#333", button_color="#444").pack(anchor="w", padx=20, pady=5)
    
    ctk.CTkLabel(cam_container, text=f"Process Every 'N' Frames\n(Higher = Less CPU, Lower = Faster Detection)", 
                 font=("Arial", 11 if is_small else 12, "bold"), text_color="gray", wraplength=wrap_len).pack(anchor="w", padx=20, pady=(15,0))

    frame_slider_var = ctk.IntVar(value=config_manager.get("process_every_n_frames"))
    frame_val_lbl = ctk.CTkLabel(cam_container, text=str(frame_slider_var.get()), font=("Arial", 14, "bold"))
    frame_val_lbl.pack(anchor="w", padx=20)
    
    def on_frame_slide(val): frame_val_lbl.configure(text=str(int(val)))
    ctk.CTkSlider(cam_container, from_=1, to=10, number_of_steps=9, variable=frame_slider_var, command=on_frame_slide, progress_color="#3498DB").pack(fill="x", padx=20, pady=5)

    
    # --- 2. Facial Recognition ---
    rec_section = ctk.CTkFrame(settings_scroll, fg_color="#E67E22", corner_radius=10, height=45)
    rec_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(rec_section, text="🧠 FACIAL RECOGNITION RULES", font=("Arial", 12 if is_small else 14, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(pady=10)

    
    rec_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    rec_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(rec_container, text="Strictness Threshold (Lower = More Strict)", 
                 font=("Arial", 11 if is_small else 12, "bold"), text_color="gray", wraplength=wrap_len).pack(anchor="w", padx=20, pady=(10,0))

    conf_slider_var = ctk.IntVar(value=config_manager.get("confidence_threshold"))
    conf_val_lbl = ctk.CTkLabel(rec_container, text=str(conf_slider_var.get()), font=("Arial", 14, "bold"))
    conf_val_lbl.pack(anchor="w", padx=20)
    
    def on_conf_slide(val): conf_val_lbl.configure(text=str(int(val)))
    ctk.CTkSlider(rec_container, from_=30, to=100, number_of_steps=70, variable=conf_slider_var, command=on_conf_slide, progress_color="#E67E22").pack(fill="x", padx=20, pady=5)





    # --- 4. Appearance Section ---
    app_section = ctk.CTkFrame(settings_scroll, fg_color="#9B59B6", corner_radius=10, height=45)
    app_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(app_section, text="🎨 APPEARANCE & THEME", font=("Arial", 12 if is_small else 14, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(pady=10)

    
    app_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    app_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    dark_mode_row = ctk.CTkFrame(app_container, fg_color="transparent")
    dark_mode_row.pack(fill="x", padx=20, pady=10)
    ctk.CTkLabel(dark_mode_row, text="Dark Mode", font=("Arial", 13, "bold"), text_color="white").pack(side="left")
    
    dark_mode_val = True if config_manager.get("appearance_mode") == "Dark" else False
    dark_mode_var = ctk.BooleanVar(value=dark_mode_val)
    ctk.CTkSwitch(dark_mode_row, text="", variable=dark_mode_var, progress_color="#9B59B6").pack(side="right")
    
    # --- 5. Attendance Tracking Period ---
    period_section = ctk.CTkFrame(settings_scroll, fg_color="#F39C12", corner_radius=10, height=45)
    period_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(period_section, text="📅 ATTENDANCE TRACKING PERIOD", font=("Arial", 12 if is_small else 14, "bold"), 
                 text_color="white", wraplength=wrap_len).pack(pady=10)

    period_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    period_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(period_container, text="System Starting Date (YYYY-MM-DD)", font=("Arial", 12, "bold"), text_color="gray", wraplength=wrap_len).pack(anchor="w", padx=20, pady=(10,0))
    ctk.CTkLabel(period_container, text="All cumulative counts (Present/Absent) will start from this date.", font=("Arial", 10, "italic"), text_color="#555", wraplength=wrap_len).pack(anchor="w", padx=20)

    start_date_var = ctk.StringVar(value=config_manager.get("starting_date"))
    ctk.CTkEntry(period_container, textvariable=start_date_var, width=200, placeholder_text="e.g. 2024-01-01").pack(anchor="w", padx=20, pady=5)

    ctk.CTkLabel(period_container, text="Target Attendance Goal (%)", font=("Arial", 12, "bold"), text_color="gray", wraplength=wrap_len).pack(anchor="w", padx=20, pady=(15,0))
    
    goal_slider_var = ctk.IntVar(value=config_manager.get("attendance_goal", 80))
    goal_val_lbl = ctk.CTkLabel(period_container, text=f"{goal_slider_var.get()}%", font=("Arial", 14, "bold"))
    goal_val_lbl.pack(anchor="w", padx=20)
    
    def on_goal_slide(val): goal_val_lbl.configure(text=f"{int(val)}%")
    ctk.CTkSlider(period_container, from_=40, to=100, number_of_steps=60, variable=goal_slider_var, command=on_goal_slide, progress_color="#F39C12").pack(fill="x", padx=20, pady=5)

    # --- SAVE ---
    def save_all_settings():
        try:
            config_manager.set_val("camera_index", int(camera_idx_var.get()))
            config_manager.set_val("process_every_n_frames", int(frame_slider_var.get()))
            config_manager.set_val("confidence_threshold", int(conf_slider_var.get()))
            config_manager.set_val("starting_date", start_date_var.get().strip())
            config_manager.set_val("attendance_goal", int(goal_slider_var.get()))
            
            new_theme = "Dark" if dark_mode_var.get() else "Light"
            config_manager.set_val("appearance_mode", new_theme)
            ctk.set_appearance_mode(new_theme)
            
            config_manager.save_config()
            
            # Hot-Reload exactly the UI to inject the new styles/values
            modify_live.trigger_live_refresh()
            messagebox.showinfo("Settings Saved", "System Settings successfully updated and applied live!")
        except Exception as e:
            messagebox.showerror("Error Saving", f"Invalid input format: {e}")
    
    save_frame = ctk.CTkFrame(settings_scroll, fg_color="transparent")
    save_frame.pack(fill="x", pady=(20, 60 if is_small else 20))

    ctk.CTkButton(save_frame, text="💾 SAVE AND APPLY SETTINGS", fg_color="#2ECC71", hover_color="#27AE60", text_color="black", height=55, font=("Arial", 16, "bold"), corner_radius=12, command=save_all_settings).pack(fill="x", padx=20)
