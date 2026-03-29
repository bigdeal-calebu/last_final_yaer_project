import customtkinter as ctk
from tkinter import messagebox
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from db import check_email_exists, get_system_email_credentials, update_password_by_email
from header import create_header

class ForgotPasswordFlow:
    def __init__(self, parent_frame, on_back_to_login=None):
        self.parent_frame = parent_frame
        self.on_back_to_login = on_back_to_login
        self.generated_otp = None
        self.verified_email = None
        
        # Build UI Container
        create_header(self.parent_frame, title_text="Smart Attendance System", subtitle_text="Password Recovery")
        
        self.shadow_frame = ctk.CTkFrame(self.parent_frame, fg_color="#0f0f0f", corner_radius=40, width=540, height=640)
        self.shadow_frame.pack(expand=True, pady=20)
        self.shadow_frame.pack_propagate(False)
        
        self.card_frame = ctk.CTkFrame(self.shadow_frame, fg_color="#1f1f1f", corner_radius=30, border_width=2, border_color="#333333")
        self.card_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Back Button
        ctk.CTkButton(self.card_frame, text="← Return to Login", text_color="orange", fg_color="transparent", 
                     hover=False, font=("Arial", 12, "bold"), anchor="w", command=self.go_back).place(x=20, y=20)
                     
        # Dynamic Content Area
        self.content_area = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, pady=(60, 20), padx=30)
        
        # Render the First State
        self.render_request_otp_state()

        # Handle responsive resize
        self.parent_frame.bind("<Configure>", self.on_resize)
        self.on_resize()

    def go_back(self):
        if self.on_back_to_login:
            self.on_back_to_login()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def render_request_otp_state(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_area, text="Forgot Password?", font=("Segoe UI", 32, "bold"), text_color="#E74C3C").pack(pady=(10, 5))
        ctk.CTkLabel(self.content_area, text="Enter your registered email address to receive a\nsecure 6-digit One Time Password (OTP).", font=("Arial", 12), text_color="#AAB7B8").pack(pady=(0, 30))
        
        email_var = ctk.StringVar()
        
        ctk.CTkLabel(self.content_area, text="Email Address", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(0, 5))
        email_entry = ctk.CTkEntry(self.content_area, textvariable=email_var, placeholder_text="student@university.edu", height=50, fg_color="#252525", border_color="#333", text_color="white")
        email_entry.pack(fill="x", padx=10, pady=(0, 20))
        
        status_lbl = ctk.CTkLabel(self.content_area, text="", text_color="orange")
        status_lbl.pack(pady=(0, 10))
        
        def handle_send_otp():
            email = email_var.get().strip()
            if not email:
                status_lbl.configure(text="Please enter your email.")
                return
                
            if not check_email_exists(email):
                status_lbl.configure(text="Email not found in the student database.")
                return
                
            # Email exists. Prepare to dispatch OTP.
            sender_email, sender_pass = get_system_email_credentials()
            if not sender_email or not sender_pass:
                messagebox.showerror("System Error", "The system's SMTP email sender is not configured by the Administrator. Cannot dispatch OTP.")
                return
                
            status_lbl.configure(text="Generating OTP & connecting to server...", text_color="#3498DB")
            self.card_frame.update()
            
            # Generate 6-digit code
            self.generated_otp = str(random.randint(100000, 999999))
            self.verified_email = email
            
            # Dispatch background thread to prevent UI freezing
            def send_email_thread():
                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, sender_pass)
                    
                    msg = MIMEMultipart()
                    msg['From'] = f"Smart Attendance System <{sender_email}>"
                    msg['To'] = email
                    msg['Subject'] = "Password Reset OTP Code"
                    
                    body = f"""
                    You have requested to reset your password.
                    
                    Your secure 6-digit One Time Password (OTP) is:
                    {self.generated_otp}
                    
                    If you did not request this, please ignore this email.
                    """
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server.send_message(msg)
                    server.quit()
                    
                    # Ensure UI updates happen on main thread safely
                    self.parent_frame.after(0, self.render_verify_otp_state)
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"\n[DEVELOPER MODE] Email failed to send, but the generated OTP is: {self.generated_otp}\n")
                    def show_dev_warning():
                        status_lbl.configure(text=f"Failed to send email: {error_msg[:50]}", text_color="red")
                        messagebox.showwarning(
                            "SMTP Error (Developer Mode)", 
                            f"Gmail rejected the login. You must use a 16-character 'App Password' from your Google Account settings instead of your normal password.\n\nHowever, to let you test the app right now, I have printed the 6-digit OTP code to your terminal window! Check your terminal and enter it on the next screen."
                        )
                        self.render_verify_otp_state()
                    self.parent_frame.after(0, show_dev_warning)
            threading.Thread(target=send_email_thread, daemon=True).start()

        ctk.CTkButton(self.content_area, text="📨 SEND OTP CODE", height=55, font=("Arial", 16, "bold"), fg_color="#3498DB", hover_color="#2980B9", command=handle_send_otp).pack(fill="x", padx=10, pady=(10, 0))

    def render_verify_otp_state(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_area, text="Verify OTP", font=("Segoe UI", 32, "bold"), text_color="#2ECC71").pack(pady=(10, 5))
        ctk.CTkLabel(self.content_area, text=f"An email containing a 6-digit code has been sent to\n{self.verified_email}", font=("Arial", 12), text_color="#AAB7B8").pack(pady=(0, 20))
        
        # 2-Column inner grid for OTP and Password to stay compact
        grid_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(grid_frame, text="6-Digit OTP Code", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", pady=(0, 5))
        otp_var = ctk.StringVar()
        ctk.CTkEntry(grid_frame, textvariable=otp_var, placeholder_text="Enter 6-digit code", height=50, fg_color="#252525", border_color="#333", text_color="#F39C12", font=("Arial", 20, "bold"), justify="center").pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(grid_frame, text="Your New Password", font=("Arial", 12, "bold"), text_color="white").pack(anchor="w", pady=(0, 5))
        pass_var = ctk.StringVar()
        ctk.CTkEntry(grid_frame, textvariable=pass_var, placeholder_text="Enter new password", show="●", height=50, fg_color="#252525", border_color="#333", text_color="white").pack(fill="x", pady=(0, 20))

        def handle_reset_password():
            user_opt = otp_var.get().strip()
            new_pass = pass_var.get().strip()
            
            if not user_opt or not new_pass:
                messagebox.showerror("Error", "Please fill in both the OTP and the New Password fields.")
                return
                
            if user_opt != self.generated_otp:
                messagebox.showerror("Verification Failed", "The OTP you entered is incorrect.")
                return
                
            # OTP matches, proceed with update
            success, msg = update_password_by_email(self.verified_email, new_pass)
            if success:
                messagebox.showinfo("Success", "Your password has been reset successfully! You may now login.")
                self.go_back()
            else:
                messagebox.showerror("Database Error", msg)
                
        ctk.CTkButton(self.content_area, text="✅ VERIFY & RESET PASSWORD", height=55, font=("Arial", 16, "bold"), fg_color="#2ECC71", hover_color="#27AE60", text_color="black", command=handle_reset_password).pack(fill="x", padx=10, pady=(20, 0))
        
        # Option to resend or wrong email
        ctk.CTkButton(self.content_area, text="Return to Email Entry", fg_color="transparent", text_color="#3498DB", hover=False, command=self.render_request_otp_state).pack(pady=(15, 0))

    def on_resize(self, event=None):
        if self.shadow_frame is None or not self.shadow_frame.winfo_exists():
            return
        width = self.parent_frame.winfo_width()
        if width > 10:
            if width < 600:
                self.shadow_frame.configure(width=width - 20)
            elif width < 800:
                self.shadow_frame.configure(width=width - 80)
            else:
                self.shadow_frame.configure(width=540)
