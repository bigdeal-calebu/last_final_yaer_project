import customtkinter as ctk
from tkinter import messagebox




def show_settings_content(content_area, responsive_manager):
    """ Comprehensive system settings and configuration interface. """
    import admin_dashboard_files.config_manager as config_manager
    import modify_live
    
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=30, pady=(20, 10))
    
    ctk.CTkLabel(header_frame, text="⚙️ SYSTEM SETTINGS", 
                 font=("Segoe UI", 32, "bold"), text_color="#3b9dd8").pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Configure core application behavior. Changes apply instantly without restart.", 
                 font=("Segoe UI", 12), text_color="gray").pack(anchor="w", pady=(0, 20))
                 
    settings_scroll = ctk.CTkScrollableFrame(content_area, fg_color="transparent")
    settings_scroll.pack(fill="both", expand=True, padx=30, pady=(10, 20))
    
    # --- 1. Camera Settings ---
    cam_section = ctk.CTkFrame(settings_scroll, fg_color="#3498DB", corner_radius=10, height=45)
    cam_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(cam_section, text="🎥 CAMERA & PERFORMANCE", font=("Arial", 14, "bold"), text_color="white").pack(pady=10)
    
    cam_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    cam_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(cam_container, text="Active Camera Index", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(10,0))
    camera_idx_var = ctk.StringVar(value=str(config_manager.get("camera_index")))
    ctk.CTkOptionMenu(cam_container, variable=camera_idx_var, values=["0", "1", "2"], width=150, fg_color="#333", button_color="#444").pack(anchor="w", padx=20, pady=5)
    
    ctk.CTkLabel(cam_container, text=f"Process Every 'N' Frames (Higher = Less CPU, Lower = Faster Detection)", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15,0))
    frame_slider_var = ctk.IntVar(value=config_manager.get("process_every_n_frames"))
    frame_val_lbl = ctk.CTkLabel(cam_container, text=str(frame_slider_var.get()), font=("Arial", 14, "bold"))
    frame_val_lbl.pack(anchor="w", padx=20)
    
    def on_frame_slide(val): frame_val_lbl.configure(text=str(int(val)))
    ctk.CTkSlider(cam_container, from_=1, to=10, number_of_steps=9, variable=frame_slider_var, command=on_frame_slide, progress_color="#3498DB").pack(fill="x", padx=20, pady=5)

    
    # --- 2. Facial Recognition ---
    rec_section = ctk.CTkFrame(settings_scroll, fg_color="#E67E22", corner_radius=10, height=45)
    rec_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(rec_section, text="🧠 FACIAL RECOGNITION RULES", font=("Arial", 14, "bold"), text_color="white").pack(pady=10)
    
    rec_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    rec_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(rec_container, text="Strictness Threshold (Lower = Must look exactly like photo. 60 is recommended.)", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(10,0))
    conf_slider_var = ctk.IntVar(value=config_manager.get("confidence_threshold"))
    conf_val_lbl = ctk.CTkLabel(rec_container, text=str(conf_slider_var.get()), font=("Arial", 14, "bold"))
    conf_val_lbl.pack(anchor="w", padx=20)
    
    def on_conf_slide(val): conf_val_lbl.configure(text=str(int(val)))
    ctk.CTkSlider(rec_container, from_=30, to=100, number_of_steps=70, variable=conf_slider_var, command=on_conf_slide, progress_color="#E67E22").pack(fill="x", padx=20, pady=5)

    unknown_row = ctk.CTkFrame(rec_container, fg_color="transparent")
    unknown_row.pack(fill="x", padx=20, pady=(15, 10))
    ctk.CTkLabel(unknown_row, text="Capture Unknown Faces Tracker", font=("Arial", 12, "bold"), text_color="white").pack(side="left")
    capture_unknowns_var = ctk.BooleanVar(value=config_manager.get("capture_unknowns"))
    ctk.CTkSwitch(unknown_row, text="", variable=capture_unknowns_var, progress_color="#E67E22").pack(side="right")
    
    ctk.CTkLabel(rec_container, text="Frames captured per unknown person", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(0,0))
    unknown_frames_var = ctk.StringVar(value=str(config_manager.get("unknown_frames_to_capture")))
    ctk.CTkEntry(rec_container, textvariable=unknown_frames_var, width=100).pack(anchor="w", padx=20, pady=5)


    # --- 3. Attendance & Reporting ---
    att_section = ctk.CTkFrame(settings_scroll, fg_color="#2ECC71", corner_radius=10, height=45)
    att_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(att_section, text="⏰ ATTENDANCE THRESHOLDS", font=("Arial", 14, "bold"), text_color="black").pack(pady=10)
    
    att_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    att_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    ctk.CTkLabel(att_container, text="Late Arrival Cutoff (HH:MM:SS)", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(10,0))
    ctk.CTkLabel(att_container, text="Students arriving after this time will be flagged in Late Comers.", font=("Arial", 10, "italic"), text_color="#555").pack(anchor="w", padx=20)
    late_time_var = ctk.StringVar(value=config_manager.get("late_arrival_time"))
    ctk.CTkEntry(att_container, textvariable=late_time_var, width=200).pack(anchor="w", padx=20, pady=5)


    # --- 4. Appearance Section ---
    app_section = ctk.CTkFrame(settings_scroll, fg_color="#9B59B6", corner_radius=10, height=45)
    app_section.pack(fill="x", pady=(10, 5))
    ctk.CTkLabel(app_section, text="🎨 APPEARANCE & THEME", font=("Arial", 14, "bold"), text_color="white").pack(pady=10)
    
    app_container = ctk.CTkFrame(settings_scroll, fg_color="#1a1a1a", corner_radius=12)
    app_container.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
    
    dark_mode_row = ctk.CTkFrame(app_container, fg_color="transparent")
    dark_mode_row.pack(fill="x", padx=20, pady=10)
    ctk.CTkLabel(dark_mode_row, text="Dark Mode", font=("Arial", 13, "bold"), text_color="white").pack(side="left")
    
    dark_mode_val = True if config_manager.get("appearance_mode") == "Dark" else False
    dark_mode_var = ctk.BooleanVar(value=dark_mode_val)
    ctk.CTkSwitch(dark_mode_row, text="", variable=dark_mode_var, progress_color="#9B59B6").pack(side="right")
    
    # --- SAVE ---
    def save_all_settings():
        try:
            config_manager.set_val("camera_index", int(camera_idx_var.get()))
            config_manager.set_val("process_every_n_frames", int(frame_slider_var.get()))
            config_manager.set_val("confidence_threshold", int(conf_slider_var.get()))
            config_manager.set_val("capture_unknowns", capture_unknowns_var.get())
            config_manager.set_val("unknown_frames_to_capture", int(unknown_frames_var.get()))
            config_manager.set_val("late_arrival_time", late_time_var.get())
            
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
    save_frame.pack(fill="x", pady=(20, 20))
    ctk.CTkButton(save_frame, text="💾 SAVE AND APPLY SETTINGS", fg_color="#2ECC71", hover_color="#27AE60", text_color="black", height=55, font=("Arial", 16, "bold"), corner_radius=12, command=save_all_settings).pack(fill="x", padx=20)
