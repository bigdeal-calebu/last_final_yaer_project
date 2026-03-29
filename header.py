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
    # Main Header Frame with Premium Separator
    header_frame = ctk.CTkFrame(parent, fg_color="#101214", border_width=1, border_color="#2b2b2b") # Midnight Rich Palette
    header_frame.pack(fill="x", padx=10, pady=(5, 5)) 
    
    # 3-Column Layout: Column 1 (Title) is the only one that expands
    header_frame.columnconfigure(0, weight=0) # Logo stays fixed size
    header_frame.columnconfigure(1, weight=1) # Title takes all remaining space
    header_frame.columnconfigure(2, weight=0) # Controls stays fixed size

    # --- 1️⃣ LOGO SECTION ---
    logo_container = ctk.CTkFrame(header_frame, corner_radius=20, fg_color="#1a1c1e") # Subtle contrast for logo
    logo_container.grid(row=0, column=0, sticky="w")
    logo_container.grid_propagate(False)

    logo_label = ctk.CTkLabel(logo_container, text="")
    logo_label.place(relx=0.5, rely=0.5, anchor="center") # Centered perfectly

    tagline_label = ctk.CTkLabel(logo_container, text="", 
                                 text_color="#F5610C")
    tagline_label.place(relx=0.5, rely=0.8, anchor="center")

    # --- 2️⃣ TITLE SECTION (The "Spacer" between logo and button) ---
    title_sub_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_sub_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10) # Balanced height

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

    # --- 4️⃣ MENU HOLDER (DEDICATED FOR HAMBURGER) ---
    menu_holder = ctk.CTkFrame(header_frame, fg_color="transparent")
    menu_holder.grid(row=0, column=2, sticky="ne", padx=10, pady=10)


    import modify_live
    refresh_btn = ctk.CTkButton(
        controls_frame, text="🔄", width=30, height=30, corner_radius=15,
        fg_color="#3498DB", hover_color="#2980B9", text_color="#000000",
        font=("Arial", 12, "bold"), command=modify_live.trigger_live_refresh
    )
    refresh_btn.pack(side="right", padx=(0, 5))

    theme_btn = ctk.CTkButton(
        controls_frame, text="☀️", width=30, height=30, corner_radius=15,
        fg_color="#2ECC71", hover_color="#27AE60", text_color="#000000",
        font=("Arial", 12, "bold")
    )
    theme_btn.pack(side="right")

    # ------------------------------------------------------------------
    # update_logo_image(size)
    # PURPOSE : Load logo.png from disk and scale it to the given pixel
    #           size, then display in the logo_label widget.
    # ------------------------------------------------------------------
    def update_logo_image(size):
        try:
            path = "logo.png"
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
        
        if width < 400: # TINY MODE (Smaller Android Phones)
            # Increased wraplength to keep the phrase whole on one line
            main_title.configure(font=("Segoe UI Variable Display", 12, "bold"), wraplength=200) 
            sub_title.configure(font=("Segoe UI Variable Small", 9, "italic"), wraplength=200)
            
            # --- Grid Layout Update: Move buttons BELOW title ---
            header_frame.rowconfigure(0, weight=1)
            header_frame.rowconfigure(1, weight=1)
            
            logo_container.grid_configure(row=0, column=0, rowspan=1, sticky="w", padx=(5, 0))
            logo_container.configure(fg_color="transparent")
            title_sub_frame.grid_configure(row=0, column=1, sticky="w", pady=(8, 0), padx=(5, 0))
            controls_frame.grid_configure(row=1, column=0, columnspan=2, sticky="e", pady=(15, 10), padx=(5, 15))

            menu_holder.grid_configure(row=0, column=1, sticky="ne", pady=8, padx=12)



            
            # Subtitle stays compact
            sub_title.pack_configure(pady=(0, 2))
            
            logo_container.configure(width=58, height=85, corner_radius=29) 
            tagline_label.configure(text="", font=("Segoe UI Variable", 1)) # Hide tagline
            update_logo_image(35)
            
            # Auto-shrink all buttons
            for child in controls_frame.winfo_children():
                if isinstance(child, (ctk.CTkButton, ctk.CTkLabel)):
                    try:
                        child.configure(width=24, height=24)
                        if hasattr(child, "configure") and child.cget("text") == "☰":
                            child.configure(font=("Segoe UI", 15, "bold"))
                    except: pass

        elif width < 600: # MOBILE MODE
            main_title.configure(font=("Segoe UI Variable Display", 15, "bold"), wraplength=280) 
            sub_title.configure(font=("Segoe UI Variable Small", 11, "italic"), wraplength=280)
            
            # --- Grid Layout Update: Move buttons BELOW title ---
            header_frame.rowconfigure(0, weight=1)
            header_frame.rowconfigure(1, weight=1)
            
            logo_container.grid_configure(row=0, column=0, rowspan=1, sticky="w", padx=(8, 0))
            logo_container.configure(fg_color="transparent")
            title_sub_frame.grid_configure(row=0, column=1, sticky="w", pady=(8, 0), padx=(10, 0))
            controls_frame.grid_configure(row=1, column=0, columnspan=2, sticky="e", pady=(20, 15), padx=(10, 20))

            menu_holder.grid_configure(row=0, column=1, sticky="ne", pady=10, padx=15)



            
            sub_title.pack_configure(pady=(0, 4))

            logo_container.configure(width=76, height=95, corner_radius=38) 
            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 7, "bold")) 
            for child in controls_frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(width=28, height=28)

        elif width < 1000: # TABLET MODE
            # Reset grid to standard 1-row layout
            header_frame.rowconfigure(1, weight=0)
            logo_container.grid_configure(row=0, column=0, rowspan=1, sticky="w", padx=0)
            logo_container.configure(fg_color="#1a1c1e")
            title_sub_frame.grid_configure(row=0, column=1, sticky="nsew", pady=10, padx=10)
            controls_frame.grid_configure(row=0, column=2, sticky="e", pady=0, padx=0)
            menu_holder.grid_configure(row=0, column=2, sticky="ne", pady=10, padx=10)

            
            main_title.configure(font=("Segoe UI Variable Display", 18, "bold"), wraplength=400) 
            sub_title.configure(font=("Segoe UI Variable Small", 12, "italic"), wraplength=400)
            
            logo_container.configure(width=100, height=100, corner_radius=50)
            sub_title.pack_configure(pady=(0, 5))

            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 8, "bold"))
            update_logo_image(65)
            
            for child in controls_frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(width=32, height=32)
            
        else: # DESKTOP MODE
            # Reset grid to standard 1-row layout
            header_frame.rowconfigure(1, weight=0)
            logo_container.grid_configure(row=0, column=0, rowspan=1, sticky="w", padx=0)
            title_sub_frame.grid_configure(row=0, column=1, sticky="nsew", pady=10, padx=10)
            controls_frame.grid_configure(row=0, column=2, sticky="e", pady=0, padx=0)
            menu_holder.grid_configure(row=0, column=2, sticky="ne", pady=10, padx=10)

            
            main_title.configure(font=("Segoe UI Variable Display", 24, "bold"), wraplength=900) 
            sub_title.configure(font=("Segoe UI Variable Small", 16, "italic"), wraplength=900)
            
            logo_container.configure(width=120, height=120, corner_radius=60)
            sub_title.pack_configure(pady=(0, 5))

            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 10, "bold"))
            update_logo_image(80)
            
            for child in controls_frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(width=36, height=36)

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

    # Expose both frames so dashboard.py can use them
    header_frame.controls_frame = controls_frame
    header_frame.menu_holder = menu_holder

    return header_frame

# END create_header