import customtkinter as ctk
import register

def show_register_student_content(content_area, responsive_manager):
    """
    Mount the student registration page seamlessly inside the Admin Dashboard.
    Passes include_header=False to avoid rendering the global app-level login headers.
    """
    # Use a solid transparent frame instead of a scrollable one to avoid double-scrollbars
    # since the dashboard's main content area is already scrollable.
    wrapper = ctk.CTkFrame(content_area, fg_color="transparent")
    wrapper.pack(fill="both", expand=True)
    
    # We pass 'include_header=False' to register.py to strip away the standalone login UI elements
    # Since we aren't registering the admin user, we don't pass any login callbacks either.
    register.show_registration_page(
        wrapper, 
        on_user_login=None, 
        on_admin_login=None, 
        include_header=False
    )
