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
    # Main Header Frame - Professional Standard
    header_frame = ctk.CTkFrame(parent, fg_color="#1a1c1e", corner_radius=0)
    header_frame.pack(fill="x", padx=0, pady=0)
    header_frame.pack_propagate(True) # Ensure it collapses to content
    
    # 5-Column Layout: Logo | Title | Controls(profile) | Utility(buttons) | Menu
    for i in range(5): header_frame.columnconfigure(i, weight=0)
    header_frame.columnconfigure(1, weight=1) # Title (expands)

    # --- 1️⃣ LOGO SECTION ---
    logo_container = ctk.CTkFrame(header_frame, corner_radius=20, fg_color="#1a1c1e")
    logo_container.grid(row=0, column=0, sticky="w")
    logo_container.grid_propagate(False)

    logo_label = ctk.CTkLabel(logo_container, text="")
    logo_label.place(relx=0.5, rely=0.5, anchor="center")

    tagline_label = ctk.CTkLabel(logo_container, text="", text_color="#F5610C")
    tagline_label.place(relx=0.5, rely=0.8, anchor="center")

    # --- 2️⃣ TITLE SECTION ---
    title_sub_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_sub_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=0)

    main_title = ctk.CTkLabel(
        title_sub_frame,
        text=title_text.upper(),
        font=("Segoe UI Variable Display", 32, "bold"), # Restore BIG baseline
        text_color="darkorange",
        justify="center"
    )
    main_title.pack(fill="x", anchor="center")

    sub_title = ctk.CTkLabel(
        title_sub_frame,
        text=subtitle_text,
        font=("Segoe UI Variable Small", 16, "italic"), # Restore BIG baseline
        text_color="#2ECC71",
        justify="center"
    )
    sub_title.pack(fill="x", anchor="center", pady=(0, 2))

    # --- 3️⃣ CONTROLS — profile area (admin_dashboard adds avatar here) ---
    controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    controls_frame.grid(row=0, column=2, sticky="e", padx=(0, 2), pady=8)

    # --- 4️⃣ UTILITY — 🔄 + ☀️ buttons live here, separate from profile ---
    utility_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    utility_frame.grid(row=0, column=3, sticky="e", padx=(0, 4), pady=8)

    # --- 5️⃣ MENU HOLDER — dedicated column for ☰ hamburger ---
    menu_holder = ctk.CTkFrame(header_frame, fg_color="transparent")
    menu_holder.grid(row=0, column=4, sticky="e", padx=(0, 8), pady=8)

    # --- 6️⃣ BOTTOM NAV BAR (Shared Row for Mobile) ---
    nav_bar_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    # Will be packed only on small screens

    import modify_live
    refresh_btn = ctk.CTkButton(
        utility_frame, text="🔄", width=30, height=30, corner_radius=15,
        fg_color="#3498DB", hover_color="#2980B9", text_color="#000000",
        font=("Arial", 12, "bold"), command=modify_live.trigger_live_refresh
    )
    refresh_btn.pack(side="right", padx=(0, 5))

    theme_btn = ctk.CTkButton(
        utility_frame, text="☀️", width=30, height=30, corner_radius=15,
        fg_color="#2ECC71", hover_color="#27AE60", text_color="#000000",
        font=("Arial", 12, "bold")
    )
    theme_btn.pack(side="right")

    # ------------------------------------------------------------------
    # update_logo_image(size)
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
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # on_resize(event)
    # ------------------------------------------------------------------
    def on_resize(event):
        # Handle both real events and manual calls with the widget object
        try:
            width = event.width
        except (AttributeError, TypeError):
            try:
                width = event.winfo_width()
            except:
                return # Fallback
                
        if width < 2: return
 
        # 1. CLEAN SLATE: Forget all previous layout positions
        for child in [logo_container, title_sub_frame, utility_frame, menu_holder, controls_frame, nav_bar_frame]:
            child.grid_forget()
            child.pack_forget()

        if width < 600:     # ── MOBILE (Grid Column Stack) ───────────────────
            # BALANCED CENTERED LAYOUT
            for i in range(10): header_frame.rowconfigure(i, weight=0, minsize=0)
            for i in range(5): header_frame.columnconfigure(i, weight=1) # All columns weight 1 for centering

            # Row 0: Logo Container - EXPLICITLY CENTERED
            bp_scale = 1.6 if width >= 400 else 1.2
            update_logo_image(int(42 * bp_scale))
            logo_container.configure(width=int(56 * bp_scale), height=int(52 * bp_scale))
            # Use columnspan=5 and sticky="n" to center in the middle of the frame
            logo_container.grid(row=0, column=0, columnspan=5, sticky="n", pady=(10, 0))
            
            # Tagline (FACE ID inside logo box)
            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", int(9 * bp_scale), "bold"))
            tagline_label.place(relx=0.5, rely=0.85, anchor="center")

            # Row 1: Title (Main + Sub) - CENTERED & WRAPPED
            title_sub_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=(5, 5))
            
            # Use slightly smaller base font (13) and tighter wrapping (width-40)
            main_title.configure(font=("Segoe UI Variable Display", int(13 * bp_scale), "bold"), 
                                 wraplength=width - 40, justify="center")
            sub_title.configure(font=("Segoe UI Variable Small", int(10 * bp_scale), "italic"), 
                                wraplength=width - 40, justify="center")
            title_sub_frame.grid_propagate(True)

            # Row 2: Unified Navigation (Menu | Utility | Profile) - CENTERED HUB
            header_frame.rowconfigure(2, weight=0)

            # Clear layout and reposition all navigation controls in a centered row
            menu_holder.grid_forget()
            utility_frame.grid_forget()
            
            # Row 2: Unified Navigation (Menu | Utility | Profile) - CENTERED HUB
            header_frame.rowconfigure(2, weight=0)
            
            # Use columns 1, 2, 3 for centering the buttons
            # We already have columnconfigure(i, weight=1) for all columns
            
            # Menu (Left)
            menu_holder.grid(row=2, column=1, sticky="e", padx=5, pady=(5, 15))
            # Theme (Center)
            utility_frame.grid(row=2, column=2, sticky="n", padx=5, pady=(5, 15))
            # Profile (Right) - actually refresh_btn is in utility_frame
            # Let's adjust utility_frame to be the container for Green/Blue and Menu be separate
            
            # Clear utility frame internal packing and use grid instead
            refresh_btn.pack_forget()
            theme_btn.pack_forget()
            
            # Pack buttons inside utility_frame side-by-side
            theme_btn.pack(side="left", padx=5)
            refresh_btn.pack(side="left", padx=5)
            
            refresh_btn.configure(width=40, height=40, corner_radius=20)
            theme_btn.configure(width=40, height=40, corner_radius=20)
            
            # Ensure the hamburger button (if it exists) fits the circular style
            for child in menu_holder.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(width=40, height=40, corner_radius=20, font=("Segoe UI", 20, "bold"))

            controls_frame.grid_forget()

            header_frame.update_idletasks() 
            return

        elif width < 1000:  # ── TABLET (Horizontal Grid) ─────────────────────
            for i in range(5): header_frame.columnconfigure(i, weight=1 if i==1 else 0)
            for i in range(10): header_frame.rowconfigure(i, weight=0, minsize=0)

            logo_container.configure(width=100, height=100, corner_radius=50)
            logo_container.grid(row=0, column=0, sticky="w", padx=8, pady=8)
            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 8, "bold"))
            tagline_label.place(relx=0.5, rely=0.8, anchor="center")
            update_logo_image(65)

            title_sub_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=8)
            wl = max(200, width - 320)
            main_title.configure(font=("Segoe UI Variable Display", 18, "bold"), wraplength=wl)
            sub_title.configure(font=("Segoe UI Variable Small", 12, "italic"), wraplength=wl)

            controls_frame.grid(row=0, column=2, sticky="e", padx=2, pady=8)
            utility_frame.grid(row=0, column=3, sticky="e", padx=4, pady=8)
            menu_holder.grid(row=0, column=4, sticky="e", padx=8, pady=8)

        else:               # ── DESKTOP (Horizontal Grid) ────────────────────
            for i in range(5): header_frame.columnconfigure(i, weight=1 if i==1 else 0)
            for i in range(10): header_frame.rowconfigure(i, weight=0, minsize=0)

            logo_container.configure(width=120, height=120, corner_radius=60)
            logo_container.grid(row=0, column=0, sticky="w", padx=8, pady=8)
            tagline_label.configure(text="FACE ID", font=("Segoe UI Variable", 10, "bold"))
            tagline_label.place(relx=0.5, rely=0.8, anchor="center")
            update_logo_image(80)

            title_sub_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=8)
            wl = max(300, width - 400)
            main_title.configure(font=("Segoe UI Variable Display", 24, "bold"), wraplength=wl)
            sub_title.configure(font=("Segoe UI Variable Small", 16, "italic"), wraplength=wl)

            controls_frame.grid(row=0, column=2, sticky="e", padx=2, pady=8)
            utility_frame.grid(row=0, column=3, sticky="e", padx=4, pady=8)
            menu_holder.grid(row=0, column=4, sticky="e", padx=10, pady=8)

    def toggle_mode():
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("Dark")
            theme_btn.configure(text="☀️")

    header_frame.bind("<Configure>", on_resize)
    
    # FORCE INITIAL SNAP: Ensure mobile layout applies immediately on start
    header_frame.after(10, lambda: on_resize(header_frame)) 
    
    theme_btn.configure(command=toggle_mode)

    header_frame.controls_frame = controls_frame
    header_frame.utility_frame  = utility_frame
    header_frame.menu_holder    = menu_holder

    return header_frame

# END create_header