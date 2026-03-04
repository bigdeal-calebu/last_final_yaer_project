import customtkinter as ctk
import cv2
from PIL import Image
from admin_dashboard_files.shared import switch_camera_live, current_camera_index, get_camera_frame

def show_face_recognition_content(content_area, responsive_manager):
    ctk.CTkLabel(content_area, text="Face Recognition", font=("Segoe UI", 28, "bold"), text_color="#3b9dd8").pack(anchor="w", padx=30, pady=(30, 10))

    # ── Camera Selector Bar ────────────────────────────────────────
    cam_bar = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=10)
    cam_bar.pack(fill="x", padx=30, pady=(0, 8))

    ctk.CTkLabel(cam_bar, text="📷 Camera:", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=(15, 8), pady=8)

    cam_btn_refs = {}   

    def select_camera_fr(idx):
        switch_camera_live(idx)
        placeholder.configure(text="Switching camera...")
        if not placeholder.winfo_ismapped():
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
        for i, b in cam_btn_refs.items():
            b.configure(fg_color="#3b9dd8" if i == idx else "#333333")

    for cam_idx in range(3):
        b = ctk.CTkButton(
            cam_bar, text=f"Cam {cam_idx}",
            width=70, height=30, font=("Arial", 11, "bold"),
            fg_color="#3b9dd8" if cam_idx == current_camera_index else "#333333",
            hover_color="#2a8cc7", corner_radius=6,
            command=lambda i=cam_idx: select_camera_fr(i)
        )
        b.pack(side="left", padx=4, pady=8)
        cam_btn_refs[cam_idx] = b

    camera_frame = ctk.CTkFrame(content_area, fg_color="#1a1a1a", corner_radius=15)
    camera_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    viewport = ctk.CTkLabel(camera_frame, text="", fg_color="black", height=450, corner_radius=10)
    viewport.pack(fill="both", expand=True, padx=20, pady=20)
    
    placeholder = ctk.CTkLabel(viewport, text="Initializing Camera...", text_color="#666666", font=("Arial", 18, "bold"))
    placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    loop_active = [True]
    def on_stop():
        loop_active[0] = False
    
    content_area.stop_camera_loop = on_stop

    def update_frame():
        if not loop_active: return
        try:
            frame = get_camera_frame()
            
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Use static size to prevent Tkinter window expansion feedback loops
                img = Image.fromarray(cv2.resize(frame_rgb, (640, 480), interpolation=cv2.INTER_LINEAR))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
                
                viewport.configure(image=ctk_img)
                viewport.image = ctk_img
                if placeholder.winfo_ismapped(): placeholder.place_forget()
                
                # Use current_camera_index from shared
                from admin_dashboard_files import shared
                for i, b in cam_btn_refs.items():
                    b.configure(fg_color="#3b9dd8" if i == shared.current_camera_index else "#333333")
            else:
                if not placeholder.winfo_ismapped(): placeholder.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            import traceback
            print(f"Camera Loop Error in face_recognition: {e}")
            traceback.print_exc()
            
        if loop_active[0] and content_area.winfo_exists():
            viewport.after(33, update_frame)
    
    update_frame()
