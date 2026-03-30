import customtkinter as ctk
from tkinter import messagebox
from db import check_user, check_admin
from header import create_header

def create_login_ui(parent_frame, on_register_click=None, include_header=True, embedded=False, on_back_click=None, on_user_login_success=None, on_admin_login_success=None, on_forgot_password_click=None):

    # ================= HEADER =================
    if include_header:
        create_header(parent_frame, title_text="Smart Attendance System", subtitle_text="Login Portal")

    # ================= CONTAINER =================
    content_parent = parent_frame
    shadow_frame = None

    if not embedded:
        shadow_frame = ctk.CTkFrame(parent_frame, fg_color="#0f0f0f", corner_radius=40, width=540, height=640)
        shadow_frame.pack(expand=True, pady=10, anchor="n") # Anchor to top for mobile
        shadow_frame.pack_propagate(False)

        card_frame = ctk.CTkFrame(shadow_frame, fg_color="#1f1f1f", corner_radius=30, border_width=2, border_color="#333333")
        card_frame.pack(fill="both", expand=True, padx=15, pady=15)
        content_parent = card_frame

    # ================= BACK BUTTON =================
    back_btn = ctk.CTkButton(content_parent, text="← GO BACK", text_color="orange", fg_color="transparent", hover=False,
                             font=("Arial", 12, "bold"), anchor="w", command=on_back_click)
    back_btn.place(x=20, y=20)

    # ================= SCROLLABLE CONTENT =================
    scroll_content = ctk.CTkScrollableFrame(content_parent, fg_color="transparent", corner_radius=20)
    scroll_content.pack(fill="both", expand=True, pady=(50, 10), padx=10)

    ctk.CTkLabel(scroll_content, text="LOGIN", font=("Arial", 40, "bold"), text_color="#2ECC71").pack(pady=(10, 5))
    ctk.CTkLabel(scroll_content, text="Access your academic dashboard", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

    # ================= ROLE SELECTION =================
    role_var = ctk.StringVar(value="User")
    role_frame = ctk.CTkSegmentedButton(scroll_content, values=["User", "Admin"],
                                        variable=role_var, height=40, width=300,
                                        fg_color="#333", selected_color="#206a9c",
                                        text_color="white")
    role_frame.pack(pady=20)

    # ================= INPUTS =================
    input_frame = ctk.CTkFrame(scroll_content, fg_color="transparent")
    input_frame.pack(fill="x", padx=40) # Default padding

    login_entry_email = ctk.CTkEntry(input_frame, placeholder_text="Enter Email", height=50, fg_color="#252525",
                                     border_color="#333", text_color="#2ECC71")
    login_entry_email.pack(fill="x", pady=10)

    login_entry_password = ctk.CTkEntry(input_frame, placeholder_text="Enter Password", show="*", height=50,
                                        fg_color="#252525", border_color="#333", text_color="#2ECC71")
    login_entry_password.pack(fill="x", pady=10)

    # ================= LOGIN LOGIC =================
    def perform_login():
        email = login_entry_email.get().strip()
        password = login_entry_password.get().strip()
        role = role_var.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if role == "Admin":
            success, msg, admin_data = check_admin(email, password)
            if success:
                if on_admin_login_success:
                    on_admin_login_success(admin_data)
            else:
                messagebox.showerror("Error", msg)
        else:
            success, msg, student_data = check_user(email, password)
            if success:
                if on_user_login_success:
                    on_user_login_success(student_data)
            else:
                messagebox.showerror("Error", msg)

    # ================= LOGIN BUTTON =================
    btn_login = ctk.CTkButton(input_frame, text="LOGIN", height=55, fg_color="#206a9c", font=("Arial", 16, "bold"), command=perform_login)
    btn_login.pack(fill="x", pady=(20, 10))

    # ================= FACIAL LOGIN TOGGLE =================
    import facial_login
    def switch_to_face():
        # Restriction: Only Students (Users) can use facial login
        if role_var.get() == "Admin":
            messagebox.showwarning("Access Restricted", "Administrators are not allowed to use face login.\nPlease use your Email and Password.")
            return

        # Stop any existing camera loops
        if hasattr(parent_frame, "stop_facial_loop"):
            parent_frame.stop_facial_loop()
        
        facial_login.show_facial_login_ui(
            parent_frame, 
            on_user_success=on_user_login_success, 
            on_admin_success=on_admin_login_success, 
            on_back_to_manual=lambda: create_login_ui(parent_frame, on_register_click, False, False, on_back_click, on_user_login_success, on_admin_login_success, on_forgot_password_click)
        )

    btn_face = ctk.CTkButton(input_frame, text="📸 LOGIN WITH FACE", height=55, fg_color="#2ECC71", hover_color="#27AE60", text_color="#000000", font=("Arial", 16, "bold"), command=switch_to_face)
    btn_face.pack(fill="x", pady=(0, 10))

    # ================= FORGOT PASSWORD LINK =================
    btn_forgot = ctk.CTkButton(input_frame, text="Forgot Password?", fg_color="transparent",
                                 text_color="#F39C12", font=("Arial", 12, "bold"), hover_color="#333", command=on_forgot_password_click)
    btn_forgot.pack(pady=(0, 5))

    # ================= REGISTER LINK =================
    btn_register = ctk.CTkButton(input_frame, text="Don't have an account? Register", fg_color="transparent",
                                 text_color="#3498DB", font=("Arial", 12), command=on_register_click)
    btn_register.pack(pady=(0, 20))

    # ================= RESPONSIVENESS =================
    def on_resize(event=None):
        if shadow_frame is None or not shadow_frame.winfo_exists():
            return
            
        width = parent_frame.winfo_width()
        height = parent_frame.winfo_height()
        
        # Adjust Card Size
        if width < 500:
            shadow_frame.configure(width=width - 10, height=min(640, height - 20))
            shadow_frame.pack_configure(anchor="n", pady=(2, 10)) # Top anchor and tight margin
            input_padx = 15
            btn_font_size = 13
            title_font_size = 30
        elif width < 800:
            shadow_frame.configure(width=width - 80, height=min(640, height - 40))
            shadow_frame.pack_configure(anchor="center", pady=20)
            input_padx = 30
            btn_font_size = 14
            title_font_size = 35
        else:
            shadow_frame.configure(width=540, height=640)
            shadow_frame.pack_configure(anchor="center", pady=20)
            input_padx = 40
            btn_font_size = 16
            title_font_size = 40

        # Apply dynamic styles
        input_frame.pack_configure(padx=input_padx)
        btn_login.configure(font=("Arial", btn_font_size, "bold"))
        btn_face.configure(font=("Arial", btn_font_size, "bold"))
        role_frame.configure(width=min(300, width - 40))
        
        # Find the "LOGIN" label to adjust its font
        for child in scroll_content.winfo_children():
            if isinstance(child, ctk.CTkLabel) and child.cget("text") == "LOGIN":
                child.configure(font=("Arial", title_font_size, "bold"))

    parent_frame.bind("<Configure>", on_resize)
    on_resize()

    return shadow_frame