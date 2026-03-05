import customtkinter as ctk
from tkinter import messagebox, filedialog
from db import update_student_details, update_student_photo
from PIL import Image, ImageOps, ImageDraw
import os
import shutil

import header

# ------------------------------------------------------------------
# create_student_dashboard(parent_frame, on_logout_click, student_data)
# PURPOSE : Build the entire Student Dashboard inside parent_frame.
#           Creates a sidebar navigation (Profile, Notifications,
#           Schedule, Digital ID, Edit Details, Logout) and a scrollable
#           content area that shows the selected page.
# PARAMS  :
#   parent_frame     — root CTk window or frame to render into
#   on_logout_click  — callback called when Logout is clicked
#   student_data     — dict with student DB columns; uses defaults if None
# ------------------------------------------------------------------
def create_student_dashboard(parent_frame, on_logout_click, student_data=None):   
    # Clear existing widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Default data if none provided
    if not student_data:
        student_data = {
            "full_name": "Student Name",
            "email": "student@university.edu",
            "academic_course": "General Course",
            "registration_no": "ID-XXXX-XXXX",
            "academic_year": "Year 1",
            "department": "General Department",
            "contact_number": "+000 000 000 000",
            "image": None
        }

    # Extract data for easier access (Keys match database columns)
    name = student_data.get("name") or student_data.get("full_name", "Student Name")
    email = student_data.get("email", "N/A")
    course = student_data.get("course") or student_data.get("academic_course", "N/A")
    reg_no = student_data.get("reg_no") or student_data.get("registration_no", "N/A")
    year = student_data.get("year") or student_data.get("year_level") or student_data.get("academic_year", "N/A")
    dept = student_data.get("department", "N/A")
    program = student_data.get("program", "N/A")
    session = student_data.get("session", "N/A")
    contact = student_data.get("contact_number") or "N/A"
    
    # Image path handling - DB uses 'profile_image', fallback to others
    photo_path = student_data.get("image") or student_data.get("profile_image") or student_data.get("image_path")
    
    # 1. Main Header
    header.create_header(parent_frame, title_text="Student Portal", subtitle_text="My Dashboard")

    # 2. Body Frame (for Grid Layout)
    body_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    body_frame.pack(fill="both", expand=True)

    # Grid Layout: 2 Columns (Sidebar | Content) inside body_frame
    body_frame.columnconfigure(0, weight=0, minsize=250) # Sidebar
    body_frame.columnconfigure(1, weight=1)              # Content
    body_frame.rowconfigure(0, weight=1)

    # --- SIDEBAR (Left) - Scrollable Navigation ---
    sidebar = ctk.CTkScrollableFrame(body_frame, fg_color="#0f0f0f", corner_radius=0, width=250, scrollbar_button_color="#2ECC71")
    sidebar.grid(row=0, column=0, sticky="nsew")
    
    # Sidebar Header - Optional, or can be removed if Main Header is enough. keeping for menu title.
    # header_frame = ctk.CTkFrame(sidebar, fg_color="#0f0f0f", corner_radius=0, height=80)
    # header_frame.pack(fill="x", pady=(10, 20))
    # header_frame.pack_propagate(False)    
    # ctk.CTkLabel(header_frame, text="STUDENT PORTAL", font=("Arial", 18, "bold"),  text_color="#2ECC71").pack(pady=20)
    ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(20,10), padx=20, anchor="w")

    # --- CONTENT AREA (Right) - SCROLLABLE ---
    content_area = ctk.CTkScrollableFrame(body_frame, fg_color="#151515", corner_radius=0,
                                          scrollbar_button_color="#2ECC71",
                                          scrollbar_button_hover_color="#27ae60")
    content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # ------------------------------------------------------------------
    # clear_content()
    # PURPOSE : Destroy all widgets in the content area so a new page
    #           can be rendered cleanly without leftover widgets.
    # ------------------------------------------------------------------
    def clear_content():
        for widget in content_area.winfo_children():
            widget.destroy()
    # END clear_content

    # ------------------------------------------------------------------
    # show_header(title)
    # PURPOSE : Render a page title on the left and the student's name
    #           on the right at the top of any content page.
    # ------------------------------------------------------------------
    def show_header(title):
        # Page Header with User Info
        header_container = ctk.CTkFrame(content_area, fg_color="transparent")
        header_container.pack(fill="x", pady=(0, 20))    
        ctk.CTkLabel(header_container, text=title, 
                     font=("Arial", 32, "bold"), text_color="darkorange").pack(side="left")
        
        # User profile indicator (top right)
        user_info = ctk.CTkFrame(header_container, fg_color="transparent")
        user_info.pack(side="right")
        ctk.CTkLabel(user_info, text=f"{name}", font=("Arial", 12),text_color="gray").pack()
    # END show_header

    # ------------------------------------------------------------------
    # show_profile()
    # PURPOSE : Render the student's Profile page showing: circular photo,
    #           personal info grid, attendance statistics (4 stat cards),
    #           academic performance (GPA / Credits / Rank), and quick
    #           action buttons.
    # ------------------------------------------------------------------
    def show_profile():
        clear_content()
        show_header("STUDENT ACADEMIC PORTAL")


        # 1. Enhanced Profile Card
        profile_card = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=15,border_width=2, border_color="#2ECC71")
        profile_card.pack(fill="x", pady=(0, 20))    
        # Profile inner container
        profile_inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_inner.pack(fill="x", padx=30, pady=30)    
        # Image Placeholder (Circle) - Left side
        img_container_size = 130
        img_display_size = 120 
        
        img_frame = ctk.CTkFrame(profile_inner, width=img_container_size, height=img_container_size,corner_radius=img_container_size//2, 
                                fg_color="#0f0f0f", border_width=3, border_color="#2ECC71")
        img_frame.pack(side="left", padx=(0, 30))
        img_frame.pack_propagate(False)
        
        # Try to load student photo
        photo_loaded = False
        if photo_path and os.path.exists(photo_path):
            try:
                # Open and convert
                pil_img = Image.open(photo_path).convert("RGBA")            
                # Resize and crop to square to fill the 120x120 area
                pil_img = ImageOps.fit(pil_img, (img_display_size, img_display_size), centering=(0.5, 0.5))
                            # Create circular mask
                mask = Image.new("L", (img_display_size, img_display_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, img_display_size, img_display_size), fill=255)
                
                # Apply mask
                pil_img.putalpha(mask)
                
                profile_img = ctk.CTkImage(light_image=pil_img, 
                                          dark_image=pil_img, 
                                          size=(img_display_size, img_display_size))
                
                ctk.CTkLabel(img_frame, image=profile_img, text="").place(relx=0.5, rely=0.5, anchor="center")
                photo_loaded = True
            except Exception as e:
                print(f"Error loading student photo: {e}")
                
        if not photo_loaded:
            ctk.CTkLabel(img_frame, text="👤", font=("Arial", 50), text_color="#2ECC71").place(relx=0.5, rely=0.5, anchor="center")
        

        # Student Info - Right side
        info_container = ctk.CTkFrame(profile_inner, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True)
        
        # Name (Large, Green)
        ctk.CTkLabel(info_container, text=name, font=("Arial", 24, "bold"), 
                     text_color="#2ECC71", anchor="w").pack(fill="x", pady=(0, 10))
        
        # Info grid
        info_grid = ctk.CTkFrame(info_container, fg_color="transparent")
        info_grid.pack(fill="x")
        info_grid.columnconfigure((0, 1), weight=1)
        
        info_items = [
            ("📧 Email:", email),
            ("🎓 Course:", course),
            ("🆔 Reg No:", reg_no),
            ("📅 Year:", year),
            ("🏢 Department:", dept),
            ("🎓 Session:", session),
            ("📞 Contact:", contact)
        ]
        
        for i, (label, value) in enumerate(info_items):
            row = i // 2
            col = i % 2
            
            item_frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            item_frame.grid(row=row, column=col, sticky="w", padx=(0, 30), pady=5)
            
            ctk.CTkLabel(item_frame, text=label, font=("Arial", 11, "bold"), 
                        text_color="gray").pack(side="left", padx=(0, 5))
            ctk.CTkLabel(item_frame, text=value, font=("Arial", 11), 
                        text_color="white").pack(side="left")


        # 2. Attendance Statistics Section
        stats_header = ctk.CTkFrame(content_area, fg_color="#2ECC71", corner_radius=10, height=45)
        stats_header.pack(fill="x", pady=(20, 15))
        ctk.CTkLabel(stats_header, text="📊 ATTENDANCE STATISTICS", 
                     font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        # Stats Grid (4 colored cards)
        stats_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.columnconfigure((0,1,2,3), weight=1)
        
        stats_data_items = [
            ("Total Present", "45 days", "#2ECC71", "✅"),
            ("Absent Days", "2 days", "#e74c3c", "❌"),
            ("Late Arrivals", "3 times", "#F39C12", "⏰"),
            ("Today's Status", "Present", "#3498db", "📍")
        ]
        
        for i, (label, value, color, icon) in enumerate(stats_data_items):
            card = ctk.CTkFrame(stats_frame, fg_color="#1f1f1f", border_width=2, 
                               border_color=color, corner_radius=12, height=120)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            card.pack_propagate(False)
            
            # Icon and label
            ctk.CTkLabel(card, text=f"{icon} {label}", text_color="gray", 
                        font=("Arial", 11, "bold")).pack(pady=(15, 5))
            
            # Value - large and colored
            ctk.CTkLabel(card, text=value, text_color=color, 
                        font=("Arial", 22, "bold")).pack(pady=5)


        # 4. Quick Actions Section
        actions_header = ctk.CTkFrame(content_area, fg_color="#9B59B6", corner_radius=10, height=45)
        actions_header.pack(fill="x", pady=(20, 15))
        ctk.CTkLabel(actions_header, text="⚡ QUICK ACTIONS", 
                     font=("Arial", 18, "bold"), text_color="white").pack(pady=10)
        
        # Action buttons grid
        actions_grid = ctk.CTkFrame(content_area, fg_color="transparent")
        actions_grid.pack(fill="x", pady=(0, 30))
        actions_grid.columnconfigure((0, 1, 2), weight=1)
        
        action_buttons = [
            ("📥 Download Transcript", "#3498db"),
            ("📧 Contact Advisor", "#2ECC71"),
            ("📝 Course Registration", "#F39C12")
        ]
        
        for i, (text_btn, color) in enumerate(action_buttons):
            btn = ctk.CTkButton(actions_grid, text=text_btn, fg_color=color, 
                               hover_color="#2c3e50", height=50, 
                               font=("Arial", 13, "bold"), corner_radius=8)
            btn.grid(row=0, column=i, padx=8, sticky="ew")
    # END show_profile


    # ------------------------------------------------------------------
    # show_notifications()
    # PURPOSE : Render the Notifications page listing system announcements
    #           with colour-coded accent bars, professional styling, and an
    #           active search/filter bar to browse by date or keywords.
    # ------------------------------------------------------------------
    def show_notifications():
        clear_content()
        show_header("NOTIFICATIONS")
        
        # Main Outer Container (Centered, max width)
        notif_container = ctk.CTkFrame(content_area, fg_color="transparent")
        notif_container.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        # --- Top Controls Frame (Search Bar & Mark Read) ---
        controls_frame = ctk.CTkFrame(notif_container, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Left side: Search / Filter Bar
        search_frame = ctk.CTkFrame(controls_frame, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#444")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(15, 5))
        # Removed StringVar so the placeholder text natively displays
        search_entry = ctk.CTkEntry(search_frame, 
                                  placeholder_text="Search by Topic (e.g., 'Exam'), Date (e.g., '25 Oct'), or Keywords...", 
                                  height=45, font=("Arial", 14), fg_color="transparent", border_width=0, text_color="white")
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        # Right side: Mark Read and Clear
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # We will populate the label and buttons dynamically based on unread count
        count_lbl = ctk.CTkLabel(buttons_frame, text="", font=("Segoe UI", 14, "bold"), text_color="#f39c12")
        count_lbl.pack(side="left", padx=(0, 15))

        clear_all_btn = ctk.CTkButton(buttons_frame, text="🗑️ Clear All", fg_color="#E74C3C", 
                      text_color="white", hover_color="#c0392b", height=40, font=("Segoe UI", 12, "bold"), corner_radius=8)
        clear_all_btn.pack(side="left", padx=(0, 10))

        # --- Premium Scrollable List Container ---
        # Dark distinct background so that individual cards hover cleanly inside it
        list_container = ctk.CTkScrollableFrame(notif_container, fg_color="#121212", corner_radius=15, scrollbar_button_color="#444", scrollbar_button_hover_color="#f39c12")
        list_container.pack(fill="both", expand=True, pady=(10, 0))

        # Database Fetch
        from db import get_student_announcements, delete_announcement_for_student
        
        # Helper to re-fetch and render
        def refresh_notifications():
            # Get fresh data for the logged in student
            all_db = get_student_announcements(student_data['registration_no'])
            render_notifications(all_db, search_entry.get())

        def delete_notif(announcement_id):
            if delete_announcement_for_student(student_data['registration_no'], announcement_id):
                refresh_notifications()
                
        def clear_all_notifs():
            all_db = get_student_announcements(student_data['registration_no'])
            for row in all_db:
                delete_announcement_for_student(student_data['registration_no'], row['id'])
            refresh_notifications()
            
        clear_all_btn.configure(command=clear_all_notifs)

        def render_notifications(all_db_announcements, search_query=""):
            # Clear current list
            for widget in list_container.winfo_children():
                widget.destroy()

            # Update count label
            total_count = len(all_db_announcements)
            if total_count > 0:
                count_lbl.configure(text=f"{total_count} Unread")
                clear_all_btn.configure(state="normal", fg_color="#E74C3C")
            else:
                count_lbl.configure(text="0 Unread")
                clear_all_btn.configure(state="disabled", fg_color="#333")

            if not all_db_announcements:
                empty_frame = ctk.CTkFrame(list_container, fg_color="transparent")
                empty_frame.pack(fill="both", expand=True, pady=100)
                ctk.CTkLabel(empty_frame, text="📭", font=("Segoe UI Emoji", 48)).pack()
                ctk.CTkLabel(empty_frame, text="You're all caught up!", font=("Segoe UI", 20, "bold"), text_color="white").pack(pady=(15, 5))
                ctk.CTkLabel(empty_frame, text="No new notifications available for you right now.", font=("Segoe UI", 14), text_color="#777").pack()
                return

            # Filter data based on search bar
            filtered_data = []
            query = search_query.lower()
            for row in all_db_announcements:
                time_str = row['created_at'].strftime("%B %d, %Y • %I:%M %p") if row.get('created_at') else "Just Now"
                searchable_text = f"{row['title']} {row['message']} {time_str}".lower()
                
                if query in searchable_text:
                    filtered_data.append({
                        "id": row['id'],
                        "title": row['title'],
                        "msg": row['message'],
                        "time": time_str,
                        # Premium colors
                        "color": "#F39C12" if row['audience'] == "All Users" else "#00E5FF",
                        "icon": "🔔" if row['audience'] == "All Users" else "👨‍🎓"
                    })

            if not filtered_data:
                ctk.CTkLabel(list_container, text=f"No results found for '{search_query}'", font=("Segoe UI", 16), text_color="#777").pack(pady=40)
                return

            # Render Filtered List
            for notif in filtered_data:
                # Premium Card Wrapper to add padding INSIDE the scroll box edges
                card_wrapper = ctk.CTkFrame(list_container, fg_color="transparent")
                card_wrapper.pack(fill="x", padx=15, pady=8)

                card = ctk.CTkFrame(card_wrapper, fg_color="#1E1E24", corner_radius=12, border_width=1, border_color="#333333")
                card.pack(fill="both", expand=True, ipady=10)
                
                # Left Color Accent Bar
                accent = ctk.CTkFrame(card, fg_color=notif['color'], width=6, corner_radius=0)
                accent.pack(side="left", fill="y", padx=(2,0), pady=2) 
                
                # Icon Box with Soft Background matching accent design
                icon_parent = ctk.CTkFrame(card, fg_color="transparent", width=80)
                icon_parent.pack(side="left", fill="y", padx=15)
                
                icon_bg = ctk.CTkFrame(icon_parent, fg_color="#2A2A35", corner_radius=15, width=50, height=50)
                icon_bg.place(relx=0.5, rely=0.5, anchor="center")
                icon_bg.pack_propagate(False)
                ctk.CTkLabel(icon_bg, text=notif['icon'], font=("Segoe UI Emoji", 24)).place(relx=0.5, rely=0.5, anchor="center")
                
                # Text Content Container
                content_frame = ctk.CTkFrame(card, fg_color="transparent")
                content_frame.pack(side="left", fill="both", expand=True, pady=15, padx=(0, 25))
                
                # Header Row (Title & Time & Delete Btn)
                row1 = ctk.CTkFrame(content_frame, fg_color="transparent")
                row1.pack(fill="x")
                ctk.CTkLabel(row1, text=notif['title'], font=("Segoe UI", 18, "bold"), text_color="white").pack(side="left")
                
                # Delete Btn (Rightmost)
                del_btn = ctk.CTkButton(row1, text="✕", width=30, height=30, fg_color="transparent", text_color="#888", hover_color="#E74C3C", corner_radius=5,
                                        command=lambda nid=notif['id']: delete_notif(nid))
                del_btn.pack(side="right", padx=(10, 0))

                # Time pill
                time_pill = ctk.CTkFrame(row1, fg_color="#2D2D3A", corner_radius=10, height=28)
                time_pill.pack(side="right")
                time_pill.pack_propagate(False)
                ctk.CTkLabel(time_pill, text=f"🕒 {notif['time']}", font=("Segoe UI", 11, "bold"), text_color="#A0A0B0").pack(padx=12, pady=3)
                
                # Message Body - dynamic wrapping to avoid breaking layout
                msg_lbl = ctk.CTkLabel(content_frame, text=notif['msg'], font=("Segoe UI", 14), text_color="#A0A0B0", justify="left")
                msg_lbl.pack(anchor="w", pady=(8,0), fill="x", expand=True)
                
                # Dynamic wrap-length binding. When the frame resizes, the text gracefully breaks.
                def resize_text(event, lbl=msg_lbl):
                    if event.width > 20: lbl.configure(wraplength=event.width - 20)
                content_frame.bind("<Configure>", resize_text)

        # Re-render list whenever search box is typed into
        def on_search_change(event=None):
            refresh_notifications()
            
        search_entry.bind('<KeyRelease>', on_search_change)

        # Initial Render
        refresh_notifications()

    # END show_notifications



    # ------------------------------------------------------------------
    # show_schedule()
    # PURPOSE : Render the student's Weekly Schedule as a timetable grid
    #           (time slots vs weekdays) with colour-coded class blocks.
    # ------------------------------------------------------------------
    def show_schedule():
        clear_content()
        show_header("MY WEEKLY SCHEDULE")
        
        schedule_frame = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=15)
        schedule_frame.pack(fill="both", expand=True)
        
        # Days Header
        days = ["TIME", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        header_row = ctk.CTkFrame(schedule_frame, fg_color="#2c3e50", height=40, corner_radius=5)
        header_row.pack(fill="x", padx=10, pady=10)
        
        for d in days:
            f = ctk.CTkFrame(header_row, fg_color="transparent")
            f.pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(f, text=d, font=("Arial", 11, "bold"), text_color="white").pack(pady=5)
            
        # Timetable Grid
        times = ["08:00 - 10:00", "10:00 - 12:00", "13:00 - 15:00", "15:00 - 17:00"]
        
        # Mock Schedule Data
        classes = {
            "MONDAY": {0: "Software Eng.\n(Lab 1)", 2: "Database Systems\n(Hall A)"},
            "TUESDAY": {1: "Web Dev\n(Lab 2)"},
            "WEDNESDAY": {0: "Algorithms\n(Hall B)", 3: "Ethics\n(Room 101)"},
            "THURSDAY": {1: "Networking\n(Lab 3)", 2: "Calculus II\n(Hall C)"},
            "FRIDAY": {0: "Project Mgmt\n(Room 202)"}
        }
        
        for i, time_slot in enumerate(times):
            row = ctk.CTkFrame(schedule_frame, fg_color="transparent" if i%2==0 else "#252525")
            row.pack(fill="x", padx=10, pady=2)
            
            # Time Column
            time_cell = ctk.CTkFrame(row, fg_color="transparent", width=100)
            time_cell.pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(time_cell, text=time_slot, font=("Arial", 11, "bold"), text_color="#2ECC71").pack(pady=10)
            
            # Day Columns
            for day in days[1:]: # Skip TIME
                cell = ctk.CTkFrame(row, fg_color="transparent", border_width=1, border_color="#333")
                cell.pack(side="left", expand=True, fill="both", padx=2)
                
                # Check if class exists
                class_name = classes.get(day, {}).get(i, "")
                if class_name:
                    inner = ctk.CTkFrame(cell, fg_color="#2980b9", corner_radius=5)
                    inner.pack(fill="both", expand=True, padx=5, pady=5)
                    ctk.CTkLabel(inner, text=class_name, font=("Arial", 10), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
    # END show_schedule


    # ------------------------------------------------------------------
    # show_digital_id()
    # PURPOSE : Render the student's Digital ID Card in the style of a
    #           KIU physical ID card: green/yellow header, photo, fields,
    #           footer with dates, signature placeholder, and fake QR code.
    # ------------------------------------------------------------------
    def show_digital_id():
        clear_content()
        show_header("DIGITAL ID CARD")
        
        # ID Card Container (Centered)
        id_container = ctk.CTkFrame(content_area, fg_color="transparent")
        id_container.pack(fill="both", expand=True)
        
        # The Card - KIU Style Design (Refined)
        # Aspect Ratio ~ 8.6cm x 5.4cm (Standard ID-1)
        card_width = 500
        card_height = 315
        
        card = ctk.CTkFrame(id_container, fg_color="white", width=card_width, height=card_height, corner_radius=12, border_width=0)
        card.place(relx=0.5, rely=0.35, anchor="center")
        card.pack_propagate(False)
        
        # --- Card Header (Green with Yellow Slant) ---
        # Main Green Header - Slightly lighter green to match image
        header_green = "#4CAF50" # Adjust if needed, 4CAF50 is decent match
        header_bg = ctk.CTkFrame(card, fg_color=header_green, height=65, corner_radius=0)
        header_bg.place(relx=0, rely=0, relwidth=0.75)
        
        # Yellow Slant Element (Simulated with Frame) - sharper angle simulation
        slant = ctk.CTkFrame(card, fg_color="#FFEB3B", height=65, width=40, corner_radius=0)
        slant.place(relx=0.72, rely=0) 
        
        # Rest of Header (White with Green Text)
        header_right = ctk.CTkFrame(card, fg_color="white", height=65, width=150, corner_radius=0)
        header_right.place(relx=0.76, rely=0, relwidth=0.24)
        
        ctk.CTkLabel(header_right, text="STUDENT IDENTITY CARD", font=("Arial", 9, "bold"), text_color="#2E7D32").place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo Text
        ctk.CTkLabel(header_bg, text="KIU", font=("Arial Black", 26, "bold"), text_color="white").place(relx=0.18, rely=0.45, anchor="center")
        ctk.CTkLabel(header_bg, text="KAMPALA\nINTERNATIONAL\nUNIVERSITY", font=("Arial", 8, "bold"), text_color="white", justify="left").place(relx=0.45, rely=0.45, anchor="center")

        # --- Photo Section ---
        # Green border box
        photo_border = ctk.CTkFrame(card, fg_color="transparent", width=125, height=145, border_width=2, border_color="#2E7D32", corner_radius=0)
        photo_border.place(relx=0.06, rely=0.28)
        
        # Inner Photo
        photo_frame = ctk.CTkFrame(photo_border, fg_color="#ecf0f1", width=115, height=135, corner_radius=0)
        photo_frame.place(relx=0.5, rely=0.5, anchor="center")
        photo_frame.pack_propagate(False)

        if photo_path and os.path.exists(photo_path):
             try:
                pil = Image.open(photo_path)
                pil = ImageOps.fit(pil, (115, 135), centering=(0.5, 0.5))
                ctk_img = ctk.CTkImage(pil, size=(115, 135))
                ctk.CTkLabel(photo_frame, image=ctk_img, text="").pack(expand=True, fill="both")
             except: 
                 pass
        else:
             ctk.CTkLabel(photo_frame, text="NO PHOTO", font=("Arial", 10)).place(relx=0.5, rely=0.5, anchor="center")
        
        # --- Details Section ---
        info_x = 0.38
        start_y = 0.30
        line_spacing = 0.10
        
        # Styles - Darker text for realism
        label_font = ("Arial", 11, "bold")
        val_font = ("Arial", 11)
        val_color = "#2c3e50"
        
        # Loop to create fields
        details = [
            ("Reg No:", reg_no),
            ("Name:", name),
            ("Course:", course),
            ("Dept:", dept),
            ("Col/Sch:", "SOMAC") 
        ]
        
        for i, (lbl, val) in enumerate(details):
            y = start_y + (i * line_spacing)
            ctk.CTkLabel(card, text=lbl, font=label_font, text_color="black", anchor="w").place(relx=info_x, rely=y)
            # Value with hanging indent
            ctk.CTkLabel(card, text=val, font=val_font, text_color=val_color, anchor="w", wraplength=190, justify="left").place(relx=info_x + 0.16, rely=y)

        # --- Footer ---
        footer_bg = ctk.CTkFrame(card, fg_color=header_green, height=45, corner_radius=0)
        footer_bg.place(relx=0, rely=0.86, relwidth=1)
        
        # Yellow Slant at bottom
        footer_slant = ctk.CTkFrame(card, fg_color="#FFEB3B", height=45, width=40, corner_radius=0)
        footer_slant.place(relx=0.65, rely=0.86)

        # Dates
        ctk.CTkLabel(footer_bg, text=f"Date Issued: 28/11/{int(year.split('-')[0])-1 if '-' in str(year) else '2025'}", font=("Arial", 9, "bold"), text_color="white").place(relx=0.05, rely=0.2)
        ctk.CTkLabel(footer_bg, text="Validity: 01/12/2026", font=("Arial", 9, "bold"), text_color="white").place(relx=0.05, rely=0.6)
        
        # Signature (Moved slightly up to be in white area above footer)
        ctk.CTkLabel(card, text="Signature", font=("Script MT Bold", 16), text_color="#1565C0").place(relx=0.76, rely=0.76) 
        ctk.CTkLabel(card, text="Holder's Signature", font=("Arial", 6), text_color="black").place(relx=0.76, rely=0.83)
        
        # Fake QR
        qr_frame = ctk.CTkFrame(card, fg_color="white", width=40, height=40)
        qr_frame.place(relx=0.88, rely=0.84) # Overlapping footer slightly for effect
        ctk.CTkLabel(qr_frame, text="QR", font=("Arial", 9)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(id_container, text="Official University Identification", font=("Arial", 12), text_color="gray").place(relx=0.5, rely=0.6, anchor="center")
    # END show_digital_id


    # ------------------------------------------------------------------
    # show_edit_details()
    # PURPOSE : Render the Edit Details form where the student can update
    #           their email, contact number, and password. Calls
    #           update_student_details() from db.py on save.
    # ------------------------------------------------------------------
    def show_edit_details():
        clear_content()
        show_header("EDIT DETAILS")
        
        # --- Profile Photo Edit Section ---
        photo_container = ctk.CTkFrame(content_area, fg_color="transparent")
        photo_container.pack(fill="x", pady=(10, 0), padx=20)
        
        new_photo_path_var = ctk.StringVar(value="")
        current_photo = student_data.get("image") or student_data.get("profile_image") or student_data.get("image_path")
        
        img_display_size = 90
        photo_frame = ctk.CTkFrame(photo_container, width=img_display_size, height=img_display_size, corner_radius=img_display_size//2, fg_color="#0f0f0f", border_width=2, border_color="#2ECC71")
        photo_frame.pack(side="left", padx=(0, 20))
        photo_frame.pack_propagate(False)
        img_lbl = ctk.CTkLabel(photo_frame, text="👤", font=("Arial", 35), text_color="#2ECC71")
        img_lbl.place(relx=0.5, rely=0.5, anchor="center")

        def load_preview(path):
            if path and os.path.exists(path):
                try:
                    pil_img = Image.open(path).convert("RGBA")            
                    pil_img = ImageOps.fit(pil_img, (img_display_size, img_display_size), centering=(0.5, 0.5))
                    mask = Image.new("L", (img_display_size, img_display_size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, img_display_size, img_display_size), fill=255)
                    pil_img.putalpha(mask)
                    preview_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_display_size, img_display_size))
                    img_lbl.configure(image=preview_img, text="")
                    img_lbl.image = preview_img
                except Exception as e:
                    print(f"Error loading preview: {e}")

        load_preview(current_photo)

        def choose_photo():
            file_path = filedialog.askopenfilename(
                title="Select Profile Picture",
                filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
            )
            if file_path:
                new_photo_path_var.set(file_path)
                load_preview(file_path)

        photo_actions = ctk.CTkFrame(photo_container, fg_color="transparent")
        photo_actions.pack(side="left", fill="y", pady=10)
        
        ctk.CTkLabel(photo_actions, text="Update Profile Picture", font=("Arial", 14, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(photo_actions, text="Recommended size: 200x200px (JPG or PNG)", font=("Arial", 11), text_color="gray").pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(photo_actions, text="Choose Photo", fg_color="#3498db", hover_color="#2980b9", width=120, height=32, font=("Arial", 12, "bold"), command=choose_photo).pack(anchor="w")
        # ----------------------------------
        
        form_frame = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=15)
        form_frame.pack(fill="x", pady=20, padx=20)
        
        # Grid layout for form
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=2)
        
        # Fields
        fields = [
            ("Email Address", email, "email_entry"),
            ("Contact Number", contact, "contact_entry"),
            ("Change Password", "", "pass_entry")
        ]
        
        entries = {}
        
        for i, (label, val, key) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label, font=("Arial", 12, "bold"), text_color="gray").grid(row=i, column=0, padx=20, pady=(20,5), sticky="w")
            
            entry = ctk.CTkEntry(form_frame, height=40, width=300, fg_color="#2b2b2b", border_color="#333", text_color="white")
            if val != "N/A": entry.insert(0, val)
            entry.grid(row=i, column=1, padx=20, pady=(20,5), sticky="w")
            entries[key] = entry
            
        entries["pass_entry"].configure(placeholder_text="Leave empty to keep current", show="*")

        # ------------------------------------------------------------------
        # save_changes()
        # PURPOSE : Validate entries, persist data to DB, and copy/save 
        #           uploaded image to local file system. Update local 
        #           variables so the change visibly reflects immediately.
        # ------------------------------------------------------------------
        def save_changes():
            new_email = entries["email_entry"].get()
            new_contact = entries["contact_entry"].get()
            new_pass = entries["pass_entry"].get()
            selected_photo = new_photo_path_var.get()
            
            if not new_email or not new_contact:
                messagebox.showerror("Error", "Email and Contact are required!")
                return
                
            success, msg = update_student_details(reg_no, new_email, new_contact, new_pass if new_pass else None)
            
            if success:
                nonlocal email, contact, photo_path
                email = new_email
                contact = new_contact
                student_data['email'] = new_email
                student_data['contact_number'] = new_contact
                
                # Process photo if selected
                if selected_photo:
                    target_dir = os.path.join(os.path.dirname(__file__), "profile_pics")
                    os.makedirs(target_dir, exist_ok=True)
                    ext = os.path.splitext(selected_photo)[1]
                    # safe filename
                    safe_reg_no = str(reg_no).replace("/", "_").replace("\\", "_")
                    target_path = os.path.join(target_dir, f"{safe_reg_no}_profile{ext}")
                    
                    try:
                        shutil.copy2(selected_photo, target_path)
                        photo_success, photo_msg = update_student_photo(reg_no, target_path)
                        if photo_success:
                            photo_path = target_path
                            student_data['image_path'] = target_path
                            student_data['profile_image'] = target_path
                            student_data['image'] = target_path
                    except Exception as e:
                        print("Error copying/saving photo:", e)

                messagebox.showinfo("Success", "Details updated successfully!")
                show_profile() # Redirect immediately to profile to see the new image
            else:
                messagebox.showerror("Error", msg)
        # END save_changes
                
        save_btn = ctk.CTkButton(content_area, text="SAVE CHANGES", fg_color="#2ECC71", hover_color="#27ae60", height=45, width=200, command=save_changes)
        save_btn.pack(pady=30)
    # END show_edit_details


    # ------------------------------------------------------------------
    # show_page(page_name)
    # PURPOSE : Generic placeholder page renderer for menu items that
    #           have not yet been fully implemented.
    # ------------------------------------------------------------------
    def show_page(page_name):
        clear_content()
        show_header(page_name.upper())
        
        # Placeholder content for other pages
        container = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=15)
        container.pack(fill="both", expand=True, pady=20)
        
        ctk.CTkLabel(container, text=f"{page_name}", font=("Arial", 24, "bold"), text_color="#2ECC71").pack(pady=(50, 20))
        ctk.CTkLabel(container, text="This feature is currently under development.", font=("Arial", 14), text_color="gray").pack(pady=10)
        ctk.CTkLabel(container, text="Check back later for updates!", font=("Arial", 12), text_color="gray").pack(pady=(0, 50))
    # END show_page


    # Navigation Menu Items (Green Theme)
    menu_items = [
        ("My Profile", "👤", show_profile),
        ("Course Materials", "📚", lambda: show_page("Course Materials")),
        ("Notification Box", "🔔", show_notifications),
        ("Edit Details", "✏️", show_edit_details),
        ("Digital ID Card", "🪪", show_digital_id)
    ]
    
    for item, icon, command in menu_items:
        btn = ctk.CTkButton(sidebar, text=f"{icon} {item}", fg_color="#2ECC71", text_color="black", font=("Arial", 12, "bold"), 
                           height=45, corner_radius=5, hover_color="#27ae60",
                           anchor="w", command=command)
        btn.pack(fill="x", padx=12, pady=5)

    # Logout Button at Bottom of Sidebar
    logout_sidebar_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=70)
    logout_sidebar_frame.pack(side="bottom", fill="x", padx=12, pady=20)
    logout_sidebar_frame.pack_propagate(False)
    
    ctk.CTkButton(logout_sidebar_frame, text="🚪 LOGOUT", fg_color="#e74c3c", 
                  hover_color="#c0392b", text_color="white", 
                  font=("Arial", 13, "bold"), height=50, corner_radius=5,
                  command=on_logout_click).pack(fill="both", expand=True)

    # Initial default view
    show_profile()
# END create_student_dashboard
