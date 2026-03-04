import customtkinter as ctk
from register import show_registration_page
from login import create_login_ui
# from db import get_connection

def main():
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()
    root.title("Smart Attendance System")
    root.geometry("1100x800")

    # Main persistent container
    main_container = ctk.CTkFrame(root, fg_color="transparent")
    main_container.pack(fill="both", expand=True)

    def clear_screen():
        for widget in main_container.winfo_children():
            widget.destroy()

    def load_login():
        clear_screen()
        create_login_ui(
            main_container, 
            on_back_click=load_registration, 
            on_user_login_success=on_user_success, # Named correctly here
            on_admin_login_success=on_admin_success, # Named correctly here
            on_register_click=load_registration
        )

    def load_registration():
        clear_screen()
        # Call with main_container as root so it clears properly later
        show_registration_page(
            main_container, 
            on_user_login=load_login, 
            on_admin_login=load_login  
        )

    # Success Callbacks
    def on_user_success(data): 
        print("Student Logged In:", data)
        clear_screen()
        import student_dashboard
        student_dashboard.create_student_dashboard(main_container, on_logout_click=load_login, student_data=data)

    def on_admin_success(data): 
        print("Admin Logged In:", data)
        clear_screen()
        import admin_dashboard
        admin_dashboard.create_admin_dashboard(main_container, on_logout_click=load_login, admin_data=data)

    # Launch the app starting with registration
    # Changed 'root' to 'main_container' and matched function names
    load_registration() 
    
    root.mainloop()

if __name__ == "__main__":
    main()