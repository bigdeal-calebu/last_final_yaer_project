import customtkinter as ctk
from tkinter import messagebox, filedialog
from db import update_student_details, update_student_photo, get_student_attendance_stats
from PIL import Image, ImageOps, ImageDraw
import os
import shutil

import header

# ══════════════════════════════════════════════════════════════════════════════
# RESPONSIVE STRATEGY
#
#   tiny   < 400 px   →  Hamburger button only; sidebar pops down on click
#   mobile 400-599    →  Compact top ribbon (3×2 grid); no hamburger
#   tablet 600-999    →  Full top ribbon (6 items, 2 rows if needed)
#   desktop ≥ 1000    →  Permanent left sidebar; no top ribbon
# ══════════════════════════════════════════════════════════════════════════════


def create_student_dashboard(parent_frame, on_logout_click, student_data=None):

    # ── Clear existing content ────────────────────────────────────────
    for w in parent_frame.winfo_children():
        w.destroy()

    # ── Default student data ──────────────────────────────────────────
    if not student_data:
        student_data = {
            "full_name":      "Student Name",
            "email":          "student@university.edu",
            "academic_course": "General Course",
            "registration_no": "ID-XXXX-XXXX",
            "academic_year":  "Year 1",
            "department":     "General Department",
            "contact_number": "+000 000 000 000",
            "image":          None,
        }

    # ── Extract fields ────────────────────────────────────────────────
    name    = student_data.get("name")    or student_data.get("full_name",       "Student Name")
    email   = student_data.get("email",   "N/A")
    course  = student_data.get("course")  or student_data.get("academic_course", "N/A")
    reg_no  = student_data.get("reg_no")  or student_data.get("registration_no", "N/A")
    year    = (student_data.get("year")   or student_data.get("year_level")
               or student_data.get("academic_year", "N/A"))
    dept    = student_data.get("department", "N/A")
    session = student_data.get("session",  "N/A")
    contact = student_data.get("contact_number") or "N/A"
    photo_path = (student_data.get("image") or student_data.get("profile_image")
                  or student_data.get("image_path"))

    _state = {
        "email":      email,
        "contact":    contact,
        "photo_path": photo_path,
    }

    # ════════════════════════════════════════════════════════════════
    # 1. APP HEADER
    # ════════════════════════════════════════════════════════════════
    app_header = header.create_header(
        parent_frame,
        title_text="Student Portal",
        subtitle_text="My Dashboard"
    )

    # ════════════════════════════════════════════════════════════════
    # 2. PAGE TITLE BAR
    # ════════════════════════════════════════════════════════════════
    top_bar = ctk.CTkFrame(parent_frame, fg_color="transparent")
    top_bar.pack(fill="x", padx=8, pady=(0, 2))

    title_row = ctk.CTkFrame(top_bar, fg_color="transparent")
    title_row.pack(fill="x")

    page_title_label = ctk.CTkLabel(
        title_row, text="STUDENT PORTAL",
        font=("Segoe UI", 24, "bold"),
        text_color="darkorange", anchor="w"
    )
    page_title_label.pack(side="left", fill="x", expand=True)

    user_label = ctk.CTkLabel(
        title_row, text=name,
        font=("Segoe UI", 11), text_color="gray"
    )
    user_label.pack(side="right", padx=8)

    # ── Top ribbon: used on tiny/mobile/tablet, hidden on desktop ────
    ribbon_container = ctk.CTkFrame(
        top_bar, fg_color="#1a1c1e",
        corner_radius=10,
        border_width=1, border_color="#333"
    )
    # packed/forgotten by on_mode_change()

    ribbon_inner = ctk.CTkFrame(ribbon_container, fg_color="transparent")
    ribbon_inner.pack(fill="x", pady=4, padx=4)

    # ════════════════════════════════════════════════════════════════
    # 3. BODY FRAME
    # ════════════════════════════════════════════════════════════════
    body_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    body_frame.pack(fill="both", expand=True)

    # Sidebar: permanent on desktop, popup on tiny
    sidebar = ctk.CTkFrame(body_frame, fg_color="#1a1c1e", corner_radius=0)

    content_area = ctk.CTkScrollableFrame(
        body_frame,
        fg_color="#151515", corner_radius=0,
        scrollbar_button_color="#2ECC71",
        scrollbar_button_hover_color="#27ae60"
    )

    # ════════════════════════════════════════════════════════════════
    # 4. RESPONSIVE MANAGER
    # ════════════════════════════════════════════════════════════════
    import layout as _layout_mod

    rm = _layout_mod.ResponsiveManager(
        body_frame, sidebar, content_area,
        has_sidebar=True   # desktop will show it; small screens won't
    )

    # Hamburger lives in header controls (only visible on tiny via rm)
    rm.create_hamburger_button(app_header.controls_frame)

    # ── Page re-render tracking ───────────────────────────────────────
    _current_renderer = [None]

    def _rerender():
        if _current_renderer[0]:
            _current_renderer[0]()

    # ════════════════════════════════════════════════════════════════
    # 5. SHARED UTILITY HELPERS
    # ════════════════════════════════════════════════════════════════

    def clear_content():
        rm.hide_sidebar()
        for w in content_area.winfo_children():
            w.destroy()

    def f(key, weight="normal"):
        return rm.font(key, weight)

    def fs(key):
        return rm.fs(key)

    def show_header(title):
        wrap = (
            160 if rm.mode == "tiny" else
            220 if rm.mode == "mobile" else
            450 if rm.mode == "tablet" else 0
        )
        page_title_label.configure(
            text=title.upper(),
            font=("Segoe UI", fs("page_title"), "bold"),
            wraplength=wrap
        )

    def _draw_photo(container, path, size):
        done = False
        if path and os.path.exists(path):
            try:
                inner = size - 4
                pil  = Image.open(path).convert("RGBA")
                pil  = ImageOps.fit(pil, (inner, inner), centering=(0.5, 0.5))
                mask = Image.new("L", (inner, inner), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, inner, inner), fill=255)
                pil.putalpha(mask)
                img = ctk.CTkImage(pil, size=(inner, inner))
                ctk.CTkLabel(container, image=img, text="").place(
                    relx=0.5, rely=0.5, anchor="center"
                )
                done = True
            except Exception:
                pass
        if not done:
            ctk.CTkLabel(
                container, text="👤",
                font=("Segoe UI Emoji", size // 2 + 4),
                text_color="#2ECC71"
            ).place(relx=0.5, rely=0.5, anchor="center")

    def _section_title(parent, icon_text, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 2), padx=rm.pad(6, 8, 10, 12))
        ctk.CTkLabel(
            row, text=icon_text,
            font=("Segoe UI", fs("section"), "bold"),
            text_color=color, anchor="w"
        ).pack(side="left")
        ctk.CTkFrame(row, fg_color=color, height=2, width=140).pack(
            side="left", padx=10
        )

    def _empty_state(parent, icon, msg):
        ef = ctk.CTkFrame(parent, fg_color="transparent")
        ef.pack(fill="both", expand=True, pady=60)
        ctk.CTkLabel(ef, text=icon, font=("Segoe UI Emoji", 40)).pack()
        ctk.CTkLabel(ef, text=msg, font=("Segoe UI", 14),
                     text_color="#777").pack()

    # ════════════════════════════════════════════════════════════════
    # 6. MENU ITEMS + NAV BUILDERS
    # ════════════════════════════════════════════════════════════════

    MENU_ITEMS = [
        ("My Profile",    "👤", lambda: show_profile()),
        ("Materials",     "📚", lambda: show_page("Course Materials")),
        ("Notifications", "🔔", lambda: show_notifications()),
        ("Edit Details",  "✏️", lambda: show_edit_details()),
        ("Digital ID",    "🪪", lambda: show_digital_id()),
        ("Logout",        "🚪", on_logout_click),
    ]

    ribbon_btns = {}   # label → CTkButton for ribbon
    sidebar_btns = {}  # label → CTkButton for sidebar

    def _menu_colors(item):
        if item == "Logout":
            return "#e74c3c", "#c0392b", "white"
        return "#2ECC71", "#27ae60", "black"

    # ── Desktop sidebar (vertical stack) ─────────────────────────────
    def _build_sidebar():
        for w in sidebar.winfo_children():
            w.destroy()
        sidebar_btns.clear()

        ctk.CTkLabel(
            sidebar, text="MENU",
            font=("Segoe UI", 11, "bold"), text_color="#555"
        ).pack(pady=(16, 6), padx=14, anchor="w")

        # Student name pill
        ctk.CTkLabel(
            sidebar, text=f"👤  {name}",
            font=("Segoe UI", 11), text_color="#aaa",
            wraplength=170, justify="left"
        ).pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkFrame(sidebar, fg_color="#333", height=1).pack(
            fill="x", padx=10, pady=(0, 8)
        )

        for item, icon, cmd in MENU_ITEMS:
            fg, hover, tc = _menu_colors(item)
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {item}",
                anchor="w", fg_color=fg, text_color=tc,
                height=40,
                font=("Segoe UI", fs("body"), "bold"),
                hover_color=hover,
                command=cmd, cursor="hand2"
            )
            btn.pack(fill="x", padx=10, pady=3)
            sidebar_btns[item] = btn

    # ── Mobile/tablet ribbon (horizontal grid) ────────────────────────
    def _build_ribbon(cols):
        """Fill ribbon_inner with MENU_ITEMS in a grid of *cols* columns."""
        for w in ribbon_inner.winfo_children():
            w.destroy()
        ribbon_btns.clear()

        for c in range(cols):
            ribbon_inner.columnconfigure(c, weight=1)

        for i, (item, icon, cmd) in enumerate(MENU_ITEMS):
            fg, hover, tc = _menu_colors(item)

            lbl = icon if rm.mode == "tiny" else f"{icon} {item}"
            btn = ctk.CTkButton(
                ribbon_inner,
                text=lbl,
                fg_color=fg, text_color=tc,
                font=("Segoe UI", fs("nav"), "bold"),
                height=36, corner_radius=6,
                hover_color=hover,
                command=cmd, cursor="hand2"
            )
            btn.grid(row=i // cols, column=i % cols,
                     padx=4, pady=4, sticky="nsew")
            ribbon_btns[item] = btn

    # ── Hamburger popup sidebar (tiny mode only) ──────────────────────
    def _build_hamburger_popup():
        for w in sidebar.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            sidebar, text="MENU",
            font=("Segoe UI", 11, "bold"), text_color="#555"
        ).pack(pady=(12, 4), padx=14, anchor="w")

        for item, icon, cmd in MENU_ITEMS:
            fg, hover, tc = _menu_colors(item)
            ctk.CTkButton(
                sidebar,
                text=f"{icon}  {item}",
                anchor="w", fg_color=fg, text_color=tc,
                height=40,
                font=("Segoe UI", fs("body"), "bold"),
                hover_color=hover,
                command=cmd, cursor="hand2"
            ).pack(fill="x", padx=10, pady=3)

    # ════════════════════════════════════════════════════════════════
    # 7. MODE CHANGE CALLBACK
    # ════════════════════════════════════════════════════════════════

    def on_mode_change():
        if not (body_frame.winfo_exists() and content_area.winfo_exists()):
            return

        mode = rm.mode

        if mode == "desktop":
            # ── Desktop: permanent sidebar, hide ribbon ───────────────
            ribbon_container.pack_forget()
            rm.has_sidebar = True
            rm._apply_desktop()
            _build_sidebar()

            # Make sure hamburger is hidden
            if rm.hamburger_btn and rm.hamburger_btn.winfo_exists():
                rm.hamburger_btn.pack_forget()

        elif mode == "tiny":
            # ── Tiny: hamburger only, sidebar is a popup ──────────────
            rm.has_sidebar = False
            rm._apply_small()
            ribbon_container.pack_forget()
            _build_hamburger_popup()

            # Ensure hamburger is visible
            if rm.hamburger_btn and rm.hamburger_btn.winfo_exists():
                rm.hamburger_btn.pack(side="right", padx=8)

        else:
            # ── Mobile / tablet: horizontal ribbon, no sidebar ─────────
            rm.has_sidebar = False
            rm._apply_small()

            cols = 3 if mode == "mobile" else 6
            _build_ribbon(cols)

            ribbon_container.pack(fill="x", pady=(0, 2))

            # Hide hamburger (ribbon replaces it)
            if rm.hamburger_btn and rm.hamburger_btn.winfo_exists():
                rm.hamburger_btn.pack_forget()

        if page_title_label.winfo_exists():
            show_header(page_title_label.cget("text"))

        _rerender()

    rm.on_mode_change = on_mode_change
    
    # ── Fluid Refresh ──
    # Whenever the window is resized, we re-run the current page's display function
    # so that text wraps, grids re-flow, and internal spacing adjusts instantly.
    def on_any_resize(width):
        _rerender()

    rm.on_any_resize = on_any_resize

    # ════════════════════════════════════════════════════════════════
    # PAGE: PROFILE
    # ════════════════════════════════════════════════════════════════
    def show_profile():
        _current_renderer[0] = show_profile
        clear_content()
        rm.registered_grids = []
        show_header("STUDENT ACADEMIC PORTAL")

        small    = rm.is_small()
        portrait = rm.is_portrait()
        pad_x    = rm.pad(6, 8, 12, 16)

        # ── Profile card ──────────────────────────────────────────────
        card = ctk.CTkFrame(
            content_area, fg_color="#1a1c1e",
            corner_radius=14, border_width=1, border_color="#2ECC71"
        )
        card.pack(fill="x", pady=(4, 8), padx=pad_x)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x",
                   padx=rm.pad(10, 12, 20, 28),
                   pady=rm.pad(10, 12, 14, 18))

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))

        img_sz = 80 if small else (105 if portrait else 128)
        photo_frame = ctk.CTkFrame(
            top, width=img_sz, height=img_sz,
            corner_radius=img_sz // 2,
            fg_color="#0f0f0f",
            border_width=2, border_color="#2ECC71"
        )
        if portrait:
            photo_frame.pack(side="top", pady=(0, 10), anchor="center")
        else:
            photo_frame.pack(side="left", padx=(0, 24))
        photo_frame.pack_propagate(False)
        _draw_photo(photo_frame, _state["photo_path"], img_sz)

        name_block = ctk.CTkFrame(top, fg_color="transparent")
        name_block.pack(
            side="left" if not portrait else "top",
            fill="both", expand=True
        )
        anc = "center" if portrait else "w"
        ctk.CTkLabel(
            name_block, text=name.upper(),
            font=("Segoe UI", fs("name"), "bold"),
            text_color="#2ECC71", anchor=anc
        ).pack(fill="x")
        ctk.CTkLabel(
            name_block, text=f"REG: {reg_no}",
            font=("Segoe UI", fs("reg"), "bold"),
            text_color="#666", anchor=anc
        ).pack(fill="x")

        # ── Info grid ─────────────────────────────────────────────────
        info_grid = ctk.CTkFrame(inner, fg_color="transparent")
        info_grid.pack(fill="x")

        info_rows = [
            ("📧  Email",             _state["email"]),
            ("🎓  Course",            course),
            ("📅  Registration Year", year),
            ("🏢  Department",        dept),
            ("🏫  Current Session",   session),
            ("📞  Phone",             _state["contact"]),
        ]

        cols = 1 if small else 2
        for c in range(cols):
            info_grid.columnconfigure(c, weight=1)

        wrap = 240 if small else (320 if portrait else 420)
        for i, (lbl_text, val) in enumerate(info_rows):
            cell = ctk.CTkFrame(info_grid, fg_color="transparent")
            py   = 4 if small else 8
            cell.grid(row=i // cols, column=i % cols,
                      sticky="ew", pady=py, padx=6)

            if small:
                cell.columnconfigure(0, weight=0, minsize=110)
                cell.columnconfigure(1, weight=1)
                ctk.CTkLabel(
                    cell, text=lbl_text,
                    font=f("label", "bold"), text_color="#888", anchor="w"
                ).grid(row=0, column=0, sticky="nw", pady=(1, 0))
                ctk.CTkLabel(
                    cell, text=str(val) if val else "N/A",
                    font=f("body_bold", "bold"), text_color="#FFF",
                    anchor="e", justify="right",
                    wraplength=wrap - 120
                ).grid(row=0, column=1, sticky="ne")
            else:
                ctk.CTkLabel(
                    cell, text=lbl_text,
                    font=f("label", "bold"), text_color="#888", anchor="w"
                ).pack(fill="x")
                ctk.CTkLabel(
                    cell, text=str(val) if val else "N/A",
                    font=f("body_bold", "bold"), text_color="#FFF",
                    anchor="w", wraplength=wrap
                ).pack(fill="x", pady=(2, 0))

        # ── Attendance stats ──────────────────────────────────────────
        _section_title(content_area, "📊  ATTENDANCE", "#2ECC71")

        stats_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 4), padx=pad_x)

        stats = get_student_attendance_stats(
            student_data.get("registration_no", "N/A"), course
        )
        if stats:
            att        = str(stats.get("Classes Attended", 0))
            miss       = str(stats.get("Classes Missed",   0))
            late       = str(stats.get("Late Count",       0))
            today_info = stats.get("Today's Attendance Status", ("N/A", "gray"))
            today_v, today_c = today_info
        else:
            att = miss = late = "0"
            today_v, today_c = "N/A", "gray"

        stat_items = [
            ("ATTENDED", att,    "#2ECC71", "✅"),
            ("MISSED",   miss,   "#e74c3c", "❌"),
            ("LATE",     late,   "#F39C12", "⏰"),
            ("TODAY",    today_v, today_c,  "📍"),
        ]

        card_h = 105 if small else 120
        for lbl, val, color, icon in stat_items:
            sc = ctk.CTkFrame(
                stats_frame, fg_color="#1a1c1e",
                border_width=1, border_color=color,
                corner_radius=12, height=card_h
            )
            sc.pack_propagate(False)
            ib = ctk.CTkFrame(sc, fg_color="#0f0f0f",
                              width=34, height=34, corner_radius=17)
            ib.pack(pady=(10, 3))
            ib.pack_propagate(False)
            ctk.CTkLabel(ib, text=icon,
                         font=("Segoe UI Emoji", 13)).place(
                relx=0.5, rely=0.5, anchor="center"
            )
            ctk.CTkLabel(sc, text=lbl, text_color="#888",
                         font=f("card_label", "bold")).pack()
            ctk.CTkLabel(sc, text=val, text_color=color,
                         font=f("card_value", "bold")).pack(pady=(2, 4))

        # Register grid AFTER all children are added
        rm.register_grid(stats_frame, max_cols=4)

        # ── Quick actions ─────────────────────────────────────────────
        _section_title(content_area, "⚡  QUICK ACTIONS", "#3498db")

        act_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        act_frame.pack(fill="x", pady=(0, 14), padx=pad_x)

        btn_h = 46 if small else 52
        for btn_text, color in [
            ("📥 Download Transcript", "#3498db"),
            ("📧 Contact Advisor",     "#2ECC71"),
            ("📝 Course Registration", "#F39C12"),
        ]:
            ctk.CTkButton(
                act_frame, text=btn_text,
                fg_color=color, hover_color="#1a1c1e",
                height=btn_h,
                font=f("btn", "bold"),
                corner_radius=10,
                border_width=1, border_color="#333",
                cursor="hand2"
            )

        rm.register_grid(act_frame, max_cols=3)

    # ════════════════════════════════════════════════════════════════
    # PAGE: NOTIFICATIONS
    # ════════════════════════════════════════════════════════════════
    def show_notifications():
        _current_renderer[0] = show_notifications
        clear_content()
        show_header("NOTIFICATIONS")

        small = rm.is_small()
        pad_x = rm.pad(6, 8, 20, 32)

        outer = ctk.CTkFrame(content_area, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=pad_x, pady=(8, 16))

        ctrl = ctk.CTkFrame(outer, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0, 8))

        sf = ctk.CTkFrame(ctrl, fg_color="#1a1a1a",
                          corner_radius=10, border_width=1, border_color="#444")
        if small:
            sf.pack(fill="x", pady=(0, 6))
        else:
            sf.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkLabel(sf, text="🔍",
                     font=("Segoe UI Emoji", 14)).pack(side="left", padx=(10, 4))
        search_entry = ctk.CTkEntry(
            sf, placeholder_text="Search…",
            height=40, font=("Segoe UI", fs("entry")),
            fg_color="transparent", border_width=0, text_color="white"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        bf = ctk.CTkFrame(ctrl, fg_color="transparent")
        bf.pack(side="top" if small else "right")

        count_lbl = ctk.CTkLabel(
            bf, text="", font=("Segoe UI", 12, "bold"), text_color="#f39c12"
        )
        count_lbl.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            bf, text="🗑️ Clear All",
            fg_color="#E74C3C", text_color="white",
            hover_color="#c0392b", height=36,
            font=("Segoe UI", fs("btn"), "bold"), corner_radius=8
        )
        clear_btn.pack(side="left")

        list_frame = ctk.CTkScrollableFrame(
            outer, fg_color="#121212",
            corner_radius=12, height=460,
            scrollbar_button_color="#444",
            scrollbar_button_hover_color="#f39c12"
        )
        list_frame.pack(fill="x", expand=True, pady=(8, 0))

        from db import get_student_announcements, delete_announcement_for_student

        def refresh():
            rows = get_student_announcements(student_data["registration_no"])
            render(rows, search_entry.get())

        def delete_one(aid):
            delete_announcement_for_student(student_data["registration_no"], aid)
            refresh()

        def clear_all():
            for r in get_student_announcements(student_data["registration_no"]):
                delete_announcement_for_student(
                    student_data["registration_no"], r["id"]
                )
            refresh()

        clear_btn.configure(command=clear_all)
        search_entry.bind("<Return>",     lambda _e: refresh())
        search_entry.bind("<KeyRelease>", lambda _e: refresh())

        wrap = (
            190 if rm.mode == "tiny" else
            240 if small else
            380 if rm.is_portrait() else 520
        )

        def render(rows, filter_text=""):
            for w in list_frame.winfo_children():
                w.destroy()

            count_lbl.configure(text=f"{len(rows)} Notifications")
            clear_btn.configure(
                state="normal" if rows else "disabled",
                fg_color="#E74C3C" if rows else "#333"
            )

            if not rows:
                _empty_state(list_frame, "📭", "No new notifications.")
                return

            q     = filter_text.lower()
            shown = [r for r in rows
                     if q in r["title"].lower() or q in r["message"].lower()]
            if not shown:
                _empty_state(list_frame, "🔍", "No messages match your search.")
                return

            for row in shown:
                ml = row["message"].lower()
                if any(k in ml for k in ("urgent", "important", "alert")):
                    accent = "#e74c3c" # Red
                    ico = "⚠️"
                elif any(k in ml for k in ("holiday", "event", "break", "mid")):
                    accent = "#3498db" # Blue
                    ico = "📅"
                else:
                    accent = "#2ECC71" # Green
                    ico = "📢"

                px = 6 if rm.mode == "tiny" else 12
                # --- Compact Card with Grid Layout ---
                nc = ctk.CTkFrame(
                    list_frame, fg_color="#1a1c1e",
                    corner_radius=12, border_width=1, border_color="#2b2b2b"
                )
                nc.pack(fill="x", pady=5, padx=px)
                
                nc.columnconfigure(2, weight=1) # Main text expands
                nc.columnconfigure(3, weight=0) # Sidebar for date/delete

                # 1. Subtle Accent Bar
                ctk.CTkFrame(nc, fg_color=accent, width=4, corner_radius=2).grid(
                    row=0, column=0, rowspan=2, sticky="ns", padx=(2, 0), pady=10
                )

                # 2. Status Icon
                if rm.mode != "tiny":
                    ctk.CTkLabel(nc, text=ico, font=("Segoe UI Emoji", 16)).grid(
                        row=0, column=1, rowspan=2, padx=(12, 0)
                    )

                # 3. Content: Title (Professional Title Case)
                display_title = row["title"].title()
                ctk.CTkLabel(
                    nc, text=display_title,
                    font=f("notif_title", "bold"),
                    text_color="#FFFFFF", anchor="w"
                ).grid(row=0, column=2, sticky="nw", padx=(12, 5), pady=(8, 0))

                # 4. Content: Message
                ctk.CTkLabel(
                    nc, text=row["message"],
                    font=f("notif_body"),
                    text_color="#AAAAAA", justify="left", wraplength=wrap
                ).grid(row=1, column=2, sticky="nw", padx=(12, 5), pady=(2, 10))

                # 5. Action Side: Date (Top)
                ds = (row["created_at"].strftime("%b %d, %H:%M") 
                      if hasattr(row["created_at"], "strftime")
                      else str(row["created_at"]))
                
                ctk.CTkLabel(
                    nc, text=ds,
                    font=("Segoe UI Variable Display", 10), text_color="#555"
                ).grid(row=0, column=3, sticky="ne", padx=(0, 12), pady=(8, 0))

                # 6. Action Side: Delete (Bottom)
                ctk.CTkButton(
                    nc, text="✕", width=24, height=24,
                    fg_color="transparent", text_color="#444",
                    hover_color="#e74c3c", corner_radius=12,
                    font=("Arial", 11, "bold"),
                    command=lambda aid=row["id"]: delete_one(aid)
                ).grid(row=1, column=3, sticky="se", padx=(0, 12), pady=(0, 10))

        refresh()

    # ════════════════════════════════════════════════════════════════
    # PAGE: DIGITAL ID
    # ════════════════════════════════════════════════════════════════
    def show_digital_id():
        _current_renderer[0] = show_digital_id
        clear_content()
        show_header("DIGITAL ID CARD")

        content_area.update_idletasks()
        win_w = content_area.winfo_width()
        if win_w <= 1:
            win_w = 800

        base_w = 550
        avail  = win_w - 32
        scale  = min(1.0, max(0.48, avail / base_w))

        c_w = int(base_w * scale)
        c_h = int(340  * scale)

        container = ctk.CTkFrame(content_area, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=16)

        card = ctk.CTkFrame(
            container, fg_color="#F8F9FA",
            width=c_w, height=c_h,
            corner_radius=int(20 * scale),
            border_width=1, border_color="#ccc"
        )
        card.pack(pady=24, anchor="center")
        card.pack_propagate(False)

        hdr = ctk.CTkFrame(card, fg_color="#1a1c1e",
                           height=int(72 * scale), corner_radius=0)
        hdr.place(relx=0, rely=0, relwidth=1)

        logo = ctk.CTkFrame(hdr, fg_color="#2ECC71",
                            width=int(40 * scale), height=int(40 * scale),
                            corner_radius=int(20 * scale))
        logo.place(relx=0.07, rely=0.5, anchor="center")
        ctk.CTkLabel(
            logo, text="K",
            font=("Segoe UI", max(8, int(17 * scale)), "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            hdr, text="KAMPALA INTERNATIONAL UNIVERSITY",
            font=("Segoe UI", max(7, int(12 * scale)), "bold"),
            text_color="#2ECC71"
        ).place(relx=0.15, rely=0.35, anchor="w")
        ctk.CTkLabel(
            hdr, text="OFFICIAL STUDENT IDENTIFICATION",
            font=("Segoe UI", max(6, int(8 * scale)), "bold"),
            text_color="#777"
        ).place(relx=0.15, rely=0.68, anchor="w")

        ps = int(140 * scale)
        pb = ctk.CTkFrame(card, fg_color="#2ECC71",
                          width=ps, height=ps,
                          corner_radius=int(10 * scale))
        pb.place(relx=0.07, rely=0.28)
        pb.pack_propagate(False)

        pbg = ctk.CTkFrame(pb, fg_color="#eee",
                           corner_radius=int(7 * scale))
        pbg.pack(padx=2, pady=2, fill="both", expand=True)
        pbg.pack_propagate(False)

        loaded = False
        if _state["photo_path"] and os.path.exists(_state["photo_path"]):
            try:
                disp = ps - 10
                pil  = Image.open(_state["photo_path"])
                pil  = ImageOps.fit(pil, (disp, disp), centering=(0.5, 0.5))
                img_tk = ctk.CTkImage(pil, size=(disp, disp))
                ctk.CTkLabel(pbg, image=img_tk, text="").pack(
                    expand=True, fill="both"
                )
                loaded = True
            except Exception:
                pass
        if not loaded:
            ctk.CTkLabel(
                pbg, text="👤",
                font=("Segoe UI Emoji", max(14, int(44 * scale))),
                text_color="#ccc"
            ).place(relx=0.5, rely=0.5, anchor="center")

        dx, dy0 = 0.38, 0.33
        step    = 0.18 * scale

        def _field(label, value, y_off):
            f2 = ctk.CTkFrame(card, fg_color="transparent")
            f2.place(relx=dx, rely=dy0 + y_off)
            ctk.CTkLabel(
                f2, text=label.upper(),
                font=("Segoe UI", max(6, int(8 * scale)), "bold"),
                text_color="#999", anchor="w"
            ).pack(anchor="w")
            ctk.CTkLabel(
                f2, text=str(value).upper(),
                font=("Segoe UI", max(8, int(12 * scale)), "bold"),
                text_color="#1a1c1e", anchor="w",
                wraplength=int(c_w * 0.56)
            ).pack(anchor="w")

        _field("Full Name",          name,   0)
        _field("Registration No.",   reg_no, step)
        _field("Course of Program",  course, step * 2)

        bc = ctk.CTkFrame(card, fg_color="#ddd",
                          width=int(90 * scale), height=int(20 * scale),
                          corner_radius=2)
        bc.place(relx=0.78, rely=0.76)
        for i in range(9):
            ctk.CTkFrame(bc, fg_color="#444",
                         width=max(1, int((1 + i % 3) * scale))
                         ).pack(side="left", padx=1, fill="y", pady=2)

        ctk.CTkLabel(
            card, text="Student Signature",
            font=("Arial", max(8, int(13 * scale)), "italic"),
            text_color="#555"
        ).place(relx=0.78, rely=0.62)
        ctk.CTkFrame(card, fg_color="#bbb", height=1,
                     width=int(90 * scale)).place(relx=0.78, rely=0.70)

        footer = ctk.CTkFrame(card, fg_color="#2ECC71",
                              height=int(24 * scale), corner_radius=0)
        footer.place(relx=0, rely=0.92, relwidth=1)
        ctk.CTkLabel(
            footer,
            text="VALID UNTIL: DEC 2026  •  UNIVERSITY SECURE ACCESS CARD",
            font=("Segoe UI", max(5, int(7 * scale)), "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ════════════════════════════════════════════════════════════════
    # PAGE: EDIT DETAILS
    # ════════════════════════════════════════════════════════════════
    def show_edit_details():
        _current_renderer[0] = show_edit_details
        clear_content()
        show_header("EDIT DETAILS")

        small    = rm.is_small()
        portrait = rm.is_portrait()
        pad_x    = rm.pad(6, 8, 14, 20)

        photo_row = ctk.CTkFrame(content_area, fg_color="transparent")
        photo_row.pack(fill="x", pady=10, padx=pad_x)

        new_photo_var = ctk.StringVar(value="")
        current_photo = _state["photo_path"]

        img_sz = 72 if small else 88
        pf = ctk.CTkFrame(
            photo_row, width=img_sz, height=img_sz,
            corner_radius=img_sz // 2,
            fg_color="#0f0f0f",
            border_width=2, border_color="#2ECC71"
        )
        if portrait:
            pf.pack(side="top", pady=(0, 10), anchor="center")
        else:
            pf.pack(side="left", padx=(0, 18))
        pf.pack_propagate(False)

        img_lbl = ctk.CTkLabel(
            pf, text="👤",
            font=("Segoe UI Emoji", img_sz // 2 + 4),
            text_color="#2ECC71"
        )
        img_lbl.place(relx=0.5, rely=0.5, anchor="center")

        def load_preview(path):
            if not (path and os.path.exists(path)):
                return
            try:
                pil = Image.open(path).convert("RGBA")
                pil = ImageOps.fit(pil, (img_sz, img_sz), centering=(0.5, 0.5))
                mask = Image.new("L", (img_sz, img_sz), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, img_sz, img_sz), fill=255)
                pil.putalpha(mask)
                tk_img = ctk.CTkImage(pil, size=(img_sz, img_sz))
                img_lbl.configure(image=tk_img, text="")
                img_lbl.image = tk_img
            except Exception as exc:
                print(f"[load_preview] {exc}")

        load_preview(current_photo)

        def choose_photo():
            p = filedialog.askopenfilename(
                title="Select Profile Picture",
                filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
            )
            if p:
                new_photo_var.set(p)
                load_preview(p)

        pa  = ctk.CTkFrame(photo_row, fg_color="transparent")
        pa.pack(side="top" if portrait else "left", fill="y")
        anc = "center" if portrait else "w"

        ctk.CTkLabel(pa, text="Update Profile Picture",
                     font=f("body_bold", "bold"),
                     text_color="white").pack(anchor=anc)
        ctk.CTkLabel(pa, text="Recommended: 200×200 px (JPG / PNG)",
                     font=f("label"), text_color="gray").pack(anchor=anc, pady=(2, 8))
        ctk.CTkButton(pa, text="Choose Photo",
                      fg_color="#3498db", hover_color="#2980b9",
                      width=110, height=30,
                      font=f("btn", "bold"),
                      command=choose_photo).pack(anchor=anc)

        form_card = ctk.CTkFrame(
            content_area, fg_color="#1a1c1e",
            corner_radius=16, border_width=1, border_color="#333"
        )
        form_card.pack(fill="x", pady=10, padx=pad_x)

        fi = ctk.CTkFrame(form_card, fg_color="transparent")
        fi.pack(fill="x", padx=rm.pad(12, 14, 22, 28), pady=18)

        ctk.CTkLabel(fi, text="📝  ACCOUNT INFORMATION",
                     font=f("section", "bold"),
                     text_color="#2ECC71", anchor="w").pack(fill="x", pady=(0, 14))

        entries = {}
        fields_cfg = [
            ("Email Address",  _state["email"],   "email"),
            ("Contact Number", _state["contact"], "contact"),
            ("Change Password","",                "password"),
        ]

        for label, value, key in fields_cfg:
            grp = ctk.CTkFrame(fi, fg_color="transparent")
            grp.pack(fill="x", pady=6)
            ctk.CTkLabel(grp, text=label.upper(),
                         font=f("label", "bold"),
                         text_color="#777", anchor="w").pack(fill="x")
            entry_h = 38 if rm.mode == "tiny" else 44
            entry = ctk.CTkEntry(
                grp, height=entry_h,
                fg_color="#121212", border_color="#333",
                placeholder_text=f"Enter {label}…",
                text_color="white",
                font=f("entry")
            )
            if value:
                entry.insert(0, value)
            entry.pack(fill="x", pady=(3, 0))
            entries[key] = entry

        entries["password"].configure(
            placeholder_text="•••••••• (leave empty to keep current)",
            show="*"
        )

        def save_changes():
            new_email   = entries["email"].get().strip()
            new_contact = entries["contact"].get().strip()
            new_pass    = entries["password"].get()
            sel_photo   = new_photo_var.get()

            if not new_email or not new_contact:
                messagebox.showerror("Validation",
                                     "Email and contact number are required.")
                return

            ok, msg = update_student_details(
                reg_no, new_email, new_contact,
                new_pass if new_pass else None
            )

            if ok:
                _state["email"]   = new_email
                _state["contact"] = new_contact
                student_data["email"]          = new_email
                student_data["contact_number"] = new_contact

                if sel_photo:
                    tdir = os.path.join(os.path.dirname(__file__), "profile_pics")
                    os.makedirs(tdir, exist_ok=True)
                    ext  = os.path.splitext(sel_photo)[1]
                    safe = str(reg_no).replace("/", "_").replace("\\", "_")
                    dst  = os.path.join(tdir, f"{safe}_profile{ext}")
                    try:
                        shutil.copy2(sel_photo, dst)
                        p_ok, _ = update_student_photo(reg_no, dst)
                        if p_ok:
                            _state["photo_path"] = dst
                            for k in ("image", "profile_image", "image_path"):
                                student_data[k] = dst
                    except Exception as exc:
                        print(f"[save_changes] photo copy error: {exc}")

                messagebox.showinfo("Success", "Details updated successfully!")
                show_profile()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(
            content_area,
            text="SAVE CHANGES",
            fg_color="#2ECC71", hover_color="#27ae60",
            height=42, width=170,
            font=("Segoe UI", fs("body"), "bold"),
            command=save_changes
        ).pack(pady=12)

    # ════════════════════════════════════════════════════════════════
    # PAGE: SCHEDULE
    # ════════════════════════════════════════════════════════════════
    def show_schedule():
        _current_renderer[0] = show_schedule
        clear_content()
        show_header("MY WEEKLY SCHEDULE")

        horiz = ctk.CTkScrollableFrame(
            content_area, orientation="horizontal",
            fg_color="transparent", height=430
        )
        horiz.pack(fill="both", expand=True, padx=8, pady=10)

        sched = ctk.CTkFrame(horiz, fg_color="#1f1f1f",
                             corner_radius=12, width=800)
        sched.pack(fill="both", expand=True)
        sched.pack_propagate(False)

        days = ["TIME", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        hdr_row = ctk.CTkFrame(sched, fg_color="#2c3e50",
                               height=42, corner_radius=5)
        hdr_row.pack(fill="x", padx=8, pady=8)
        for d in days:
            cf = ctk.CTkFrame(hdr_row, fg_color="transparent")
            cf.pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(cf, text=d,
                         font=("Segoe UI", 9, "bold"),
                         text_color="white").pack(pady=4)

        times = ["08:00–10:00", "10:00–12:00", "13:00–15:00", "15:00–17:00"]
        classes = {
            "MONDAY":    {0: "Software Eng.\n(Lab 1)", 2: "Database\n(Hall A)"},
            "TUESDAY":   {1: "Web Dev\n(Lab 2)"},
            "WEDNESDAY": {0: "Algorithms\n(Hall B)", 3: "Ethics\n(Rm 101)"},
            "THURSDAY":  {1: "Networking\n(Lab 3)", 2: "Calculus II\n(Hall C)"},
            "FRIDAY":    {0: "Proj Mgmt\n(Rm 202)"},
        }

        for i, slot in enumerate(times):
            row = ctk.CTkFrame(
                sched,
                fg_color="transparent" if i % 2 == 0 else "#252525"
            )
            row.pack(fill="x", padx=8, pady=2)

            tc = ctk.CTkFrame(row, fg_color="transparent", width=110)
            tc.pack(side="left", fill="y")
            tc.pack_propagate(False)
            ctk.CTkLabel(tc, text=slot,
                         font=("Segoe UI", 8, "bold"),
                         text_color="#2ECC71").place(
                relx=0.5, rely=0.5, anchor="center"
            )

            for day in days[1:]:
                cell = ctk.CTkFrame(row, fg_color="transparent",
                                    border_width=1, border_color="#333")
                cell.pack(side="left", expand=True, fill="both", padx=2)
                cn = classes.get(day, {}).get(i, "")
                if cn:
                    inr = ctk.CTkFrame(cell, fg_color="#2980b9", corner_radius=4)
                    inr.pack(fill="both", expand=True, padx=3, pady=3)
                    ctk.CTkLabel(inr, text=cn,
                                 font=("Segoe UI", 8), text_color="white"
                                 ).place(relx=0.5, rely=0.5, anchor="center")

    # ════════════════════════════════════════════════════════════════
    # PAGE: PLACEHOLDER
    # ════════════════════════════════════════════════════════════════
    def show_page(page_name):
        clear_content()
        show_header(page_name.upper())
        c = ctk.CTkFrame(content_area, fg_color="#1f1f1f", corner_radius=12)
        c.pack(fill="both", expand=True, pady=16)
        ctk.CTkLabel(c, text=page_name,
                     font=("Segoe UI", 20, "bold"),
                     text_color="#2ECC71").pack(pady=(50, 14))
        ctk.CTkLabel(c, text="This feature is currently under development.",
                     font=("Segoe UI", 13), text_color="gray").pack(pady=6)
        ctk.CTkLabel(c, text="Check back later for updates!",
                     font=("Segoe UI", 11), text_color="gray").pack(pady=(0, 50))

    # ════════════════════════════════════════════════════════════════
    # STARTUP
    # ════════════════════════════════════════════════════════════════
    body_frame.update_idletasks()
    on_mode_change()   # set correct layout for current window size
    show_profile()     # default landing page