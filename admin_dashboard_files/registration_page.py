import customtkinter as ctk
import register

def show_register_student_content(area, rm, on_logout_click=None):
    # Header
    ctk.CTkLabel(area, text="Register New Student", font=("Segoe UI", 28, "bold"), text_color="#2ECC71").pack(anchor="w", padx=30, pady=(30, 20))
    # Note: register.show_registration_page expects on_user_login or on_admin_login, NOT on_login_click
    register.show_registration_page(area, include_header=False, on_admin_login=on_logout_click)
