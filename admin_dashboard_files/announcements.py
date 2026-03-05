import customtkinter as ctk
from tkinter import messagebox

def show_announcement_content(content_area, responsive_manager, admin_data=None):
    """Manage System Announcements"""
    # Main Header Area
    header_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    header_frame.pack(fill="x", padx=40, pady=(30, 10))
    
    ctk.CTkLabel(header_frame, text="📢 Announcements", 
                 font=("Segoe UI", 34, "bold"), text_color="#F39C12").pack(anchor="w")
    ctk.CTkLabel(header_frame, text="Broadcast important updates to users across the system.", 
                 font=("Segoe UI", 12), text_color="gray").pack(anchor="w", pady=(0, 20))

    # Form Container card (centered visually by limiting max width)
    card_container = ctk.CTkFrame(content_area, fg_color="transparent")
    card_container.pack(fill="x", expand=True, padx=40)

    announce_frame = ctk.CTkFrame(card_container, fg_color="#1f1f1f", corner_radius=16, border_width=1, border_color="#333")
    announce_frame.pack(anchor="w", fill="x", expand=False, pady=10) 
    
    # Form Content Wrapper (For clean inner padding)
    inner_padding = ctk.CTkFrame(announce_frame, fg_color="transparent")
    inner_padding.pack(fill="both", expand=True, padx=40, pady=40)

    ctk.CTkLabel(inner_padding, text="Create New Announcement", font=("Segoe UI", 20, "bold"), text_color="white").pack(anchor="w", pady=(0, 25))
    
    # Title input
    ctk.CTkLabel(inner_padding, text="Subject / Title", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    title_entry = ctk.CTkEntry(inner_padding, height=45, placeholder_text="e.g., System Maintenance Scheduled for Jan 1st", fg_color="#121212", border_color="#444", text_color="white")
    title_entry.pack(fill="x", anchor="w", pady=(0, 25))
    
    # Message Body (Textbox)
    ctk.CTkLabel(inner_padding, text="Message Body", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    msg_entry = ctk.CTkTextbox(inner_padding, height=200, fg_color="#121212", border_color="#444", border_width=1, text_color="white")
    msg_entry.pack(fill="x", anchor="w", pady=(0, 25))
    
    # Audience Select
    ctk.CTkLabel(inner_padding, text="Target Audience", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(0,5))
    
    audience_frame = ctk.CTkFrame(inner_padding, fg_color="transparent")
    audience_frame.pack(anchor="w", fill="x", pady=(0, 35))
    
    audience_opt = ctk.CTkOptionMenu(audience_frame, values=["All Users", "Students Only", "Staff Only", "Admins Only", "Specific Student"], width=250, height=40, fg_color="#333", button_color="#444", button_hover_color="#555")
    audience_opt.pack(side="left")
    
    reg_no_entry = ctk.CTkEntry(audience_frame, height=40, width=220, placeholder_text="Enter Registration No...", fg_color="#121212", border_color="#444", text_color="white")
    
    def on_audience_change(choice):
        if choice == "Specific Student":
            reg_no_entry.pack(side="left", padx=(15, 0))
        else:
            reg_no_entry.pack_forget()
            
    audience_opt.configure(command=on_audience_change)
    
    # Divider line
    divider = ctk.CTkFrame(inner_padding, height=2, fg_color="#333")
    divider.pack(fill="x", pady=(0, 25))

    from db import post_announcement as db_post, get_all_student_emails, get_student_email_by_regno
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import threading

    def send_emails_in_background(title, msg_body, audience, specific_reg_no=None):
        def _send():
            if audience == "Specific Student":
                if not specific_reg_no: return
                email = get_student_email_by_regno(specific_reg_no)
                if not email:
                    print(f"No valid email found for specific student: {specific_reg_no}")
                    return
                emails = [email]
            elif audience in ["All Users", "Students Only"]:
                emails = get_all_student_emails()
            else:
                return
            
            if not emails:
                print("No students found to send emails to.")
                return
                
            if not admin_data or not admin_data.get('email') or not admin_data.get('password'):
                print("⚠️ Admin email or password is missing in the database. Cannot send emails.")
                return
                
            SENDER_EMAIL = admin_data.get('email')
            SENDER_PASSWORD = admin_data.get('password')
            
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                
                for recipient in emails:
                    try:
                        email_msg = MIMEMultipart()
                        email_msg['From'] = SENDER_EMAIL
                        email_msg['To'] = recipient
                        email_msg['Subject'] = f"Student Portal: {title}"
                        
                        email_msg.attach(MIMEText(msg_body, 'plain'))
                        server.send_message(email_msg)
                        print(f"Sent email to {recipient}")
                    except Exception as e:
                        print(f"Failed to send to {recipient}: {e}")
                        
                server.quit()
                print("All emails processed successfully.")
            except Exception as e:
                print(f"SMTP Server Error: {e}")
                
        threading.Thread(target=_send, daemon=True).start()

    def post_announcement():
        title = title_entry.get().strip()
        msg_body = msg_entry.get("1.0", 'end').strip()
        audience = audience_opt.get()
        specific_reg_no = reg_no_entry.get().strip()
        
        db_audience = audience
        if audience == "Specific Student":
            if not specific_reg_no:
                messagebox.showerror("Error", "Registration Number is required for specific student!")
                return
            db_audience = f"Specific Student: {specific_reg_no}"
        
        if title:
            success, msg = db_post(title, msg_body, db_audience)
            if success:
                send_emails_in_background(title, msg_body, audience, specific_reg_no)
                messagebox.showinfo("Success", "Announcement posted successfully and email dispatch started!")
                title_entry.delete(0, 'end')
                msg_entry.delete("1.0", 'end')
                reg_no_entry.delete(0, 'end')
            else:
                messagebox.showerror("Database Error", msg)
        else:
            messagebox.showerror("Error", "Title is required!")

    bottom_frame = ctk.CTkFrame(inner_padding, fg_color="transparent")
    bottom_frame.pack(fill="x")
    
    submit_btn = ctk.CTkButton(bottom_frame, text="📢 POST ANNOUNCEMENT", height=45, width=220, 
                 font=("Segoe UI", 14, "bold"), fg_color="#F39C12", hover_color="#D68910", text_color="black", command=post_announcement)
    submit_btn.pack(side="right")
