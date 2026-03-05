import customtkinter as ctk
from PIL import Image
import os


# ------------------------------------------------------------------
# create_header(parent, title_text, subtitle_text)
# PURPOSE : Build and return the top header bar for any dashboard
#           page. Contains a responsive logo, a title + subtitle,
#           and a light/dark mode toggle button.
#           Automatically resizes fonts and the logo when the window
#           changes size (mobile / tablet / desktop breakpoints).
# RETURNS : header_frame  — the outer CTkFrame that holds everything.
#           header_frame.controls_frame is exposed so callers can
#           append extra widgets (e.g. admin avatar) to the right side.
# ------------------------------------------------------------------
def create_header(parent, title_text="Smart Attendance System", subtitle_text="Admin Dashboard"):
    # Main Header Frame
    header_frame = ctk.CTkFrame(parent, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(10, 5)) # Reduced outer padding for more space
    
    # 3-Column Layout: Column 1 (Title) is the only one that expands
    header_frame.columnconfigure(0, weight=0) # Logo stays fixed size
    header_frame.columnconfigure(1, weight=1) # Title takes all remaining space
    header_frame.columnconfigure(2, weight=0) # Controls stays fixed size

    # --- 1️⃣ LOGO SECTION ---
    logo_container = ctk.CTkFrame(header_frame, corner_radius=70, fg_color="#1f1f1f")
    logo_container.grid(row=0, column=0, sticky="w")
    logo_container.grid_propagate(False)

    logo_label = ctk.CTkLabel(logo_container, text="")
    logo_label.place(relx=0.5, rely=0.42, anchor="center")

    tagline_label = ctk.CTkLabel(logo_container, text="", 
                                 text_color="#F5610C", font=("Segoe UI Variable", 10, "bold"))
    tagline_label.place(relx=0.5, rely=0.8, anchor="center")

    # --- 2️⃣ TITLE SECTION (The "Spacer" between logo and button) ---
    title_sub_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_sub_frame.grid(row=0, column=1, sticky="nsew", padx=10) # Added padx to prevent touching logo/btn

    main_title = ctk.CTkLabel(
        title_sub_frame, 
        text=title_text.upper(),
        font=("Segoe UI Variable Display", 32, "bold"), 
        text_color="darkorange",
        justify="center" # Ensures text stays centered when it wraps
    )
    main_title.pack(expand=True, fill="both") 

    sub_title = ctk.CTkLabel(
        title_sub_frame, 
        text=subtitle_text,
        font=("Segoe UI Variable Small", 16, "italic"), 
        text_color="#2ECC71",
        justify="center"
    )
    sub_title.pack(expand=True, pady=(0, 5))

    # --- 3️⃣ CONTROLS ---
    controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    controls_frame.grid(row=0, column=2, sticky="e")

    import modify_live
    refresh_btn = ctk.CTkButton(
        controls_frame, text="🔄", width=40, height=40, corner_radius=20,
        fg_color="#3498DB", hover_color="#2980B9", text_color="#000000",
        font=("Arial", 14, "bold"), command=modify_live.trigger_live_refresh
    )
    refresh_btn.pack(side="right", padx=(0, 10))

    theme_btn = ctk.CTkButton(
        controls_frame, text="☀️", width=40, height=40, corner_radius=20,
        fg_color="#2ECC71", hover_color="#27AE60", text_color="#000000",
        font=("Arial", 14, "bold")
    )
    theme_btn.pack(side="right")

    # ------------------------------------------------------------------
    # update_logo_image(size)
    # PURPOSE : Load logo.png from disk and scale it to the given pixel
    #           size, then display in the logo_label widget.
    # ------------------------------------------------------------------
    def update_logo_image(size):
        try:
            path = r"C:\Users\BIGDEAL CALEBU\Desktop\2026_final_special\logo.png"
            if not os.path.exists(path): path = "logo.png"
            if os.path.exists(path):
                img = Image.open(path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                logo_label.configure(image=ctk_img)
                logo_label.image = ctk_img
        except:
            logo_label.configure(text="ID")
    # END update_logo_image

    # ------------------------------------------------------------------
    # on_resize(event)
    # PURPOSE : Respond to window <Configure> events and switch between
    #           mobile (<600px), tablet (<1000px), and desktop layouts.
    #           Adjusts font sizes, logo dimensions, and button sizes.
    # ------------------------------------------------------------------
    def on_resize(event):
        width = event.width
        
        if width < 600: # MOBILE MODE
            # A very narrow wraplength prevents overlapping logo/buttons
            main_title.configure(font=("Segoe UI Variable Display", 15, "bold"), wraplength=140) 
            sub_title.configure(font=("Segoe UI Variable Small", 10, "italic"), wraplength=140)
            
            logo_container.configure(width=75, height=90)
            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 7, "bold"))
            update_logo_image(40)
            
            theme_btn.configure(width=28, height=28)
            
        elif width < 1000: # TABLET MODE
            main_title.configure(font=("Segoe UI Variable Display", 22, "bold"), wraplength=400) 
            sub_title.configure(font=("Segoe UI Variable Small", 13, "italic"), wraplength=400)
            
            logo_container.configure(width=110, height=140)
            tagline_label.configure(text="FACE RECOGNITION", font=("Segoe UI Variable", 9, "bold"))
            update_logo_image(70)
            
            theme_btn.configure(width=35, height=35)
            
        else: # DESKTOP MODE
            main_title.configure(font=("Segoe UI Variable Display", 34, "bold"), wraplength=900) 
            sub_title.configure(font=("Segoe UI Variable Small", 18, "italic"), wraplength=900)
            
            logo_container.configure(width=150, height=180)
            tagline_label.configure(text="RECOGNITION SYSTEM", font=("Segoe UI Variable", 11, "bold"))
            update_logo_image(110)
            
            theme_btn.configure(width=45, height=45)

    header_frame.bind("<Configure>", on_resize)
    # END on_resize

    # ------------------------------------------------------------------
    # toggle_mode()
    # PURPOSE : Switch CustomTkinter appearance between Dark and Light
    #           mode and update the theme button icon accordingly.
    # ------------------------------------------------------------------
    def toggle_mode():
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("Dark")
            theme_btn.configure(text="☀️")
    # END toggle_mode
    
    theme_btn.configure(command=toggle_mode)

    # Expose controls_frame so callers (e.g. dashboard.py) can append widgets to it
    header_frame.controls_frame = controls_frame

    return header_frame
# END create_header