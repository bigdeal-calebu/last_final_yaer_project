import customtkinter as ctk
import modify_live

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
        def _rebuild():
            clear_screen()
            from login import create_login_ui
            create_login_ui(
                main_container, 
                on_back_click=load_registration, 
                on_user_login_success=on_user_success,
                on_admin_login_success=on_admin_success,
                on_register_click=load_registration,
                on_forgot_password_click=load_forgot_password
            )
        modify_live.set_refresh_action(_rebuild)
        _rebuild()

    def load_forgot_password():
        def _rebuild():
            clear_screen()
            from forgot_password import ForgotPasswordFlow
            ForgotPasswordFlow(
                main_container,
                on_back_to_login=load_login
            )
        modify_live.set_refresh_action(_rebuild)
        _rebuild()

    def load_registration():
        def _rebuild():
            clear_screen()
            from register import show_registration_page
            show_registration_page(
                main_container, 
                on_user_login=load_login, 
                on_admin_login=load_login  
            )
        modify_live.set_refresh_action(_rebuild)
        _rebuild()

    # Success Callbacks
    def on_user_success(data): 
        print("Student Logged In:", data)
        def _rebuild():
            clear_screen()
            import student_dashboard
            student_dashboard.create_student_dashboard(main_container, on_logout_click=load_login, student_data=data)
        modify_live.set_refresh_action(_rebuild)
        _rebuild()

    def on_admin_success(data): 
        print("Admin Logged In:", data)
        def _rebuild():
            clear_screen()
            import admin_dashboard
            admin_dashboard.create_admin_dashboard(main_container, on_logout_click=load_login, admin_data=data)
        modify_live.set_refresh_action(_rebuild)
        _rebuild()

    # Launch the app starting with registration
    load_registration() 
    
    root.mainloop()

if __name__ == "__main__":
    main()