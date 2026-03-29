import customtkinter as ctk


class ResponsiveManager:
    """
    Adaptive layout engine for CustomTkinter dashboards.

    ┌──────────────────────────────────────────────────────────────────┐
    │  BREAKPOINTS                                                     │
    │  tiny   : width <  400 px  →  Small phones                      │
    │  mobile : 400 – 599 px     →  Standard Android / iPhone         │
    │  tablet : 600 – 999 px     →  Tablets / small laptops           │
    │  desktop: ≥ 1000 px        →  Laptop / PC monitor               │
    │                                                                  │
    │  Layout strategy:                                                │
    │  • tiny/mobile/tablet → top nav ribbon (hamburger on tiny)       │
    │  • desktop            → permanent left sidebar (240px)           │
    └──────────────────────────────────────────────────────────────────┘
    """

    BP_TINY    = 400
    BP_MOBILE  = 600
    BP_DESKTOP = 1000

    FONT_TABLE = {
        "page_title":  (16, 18, 22, 28),
        "section":     (13, 14, 15, 18),
        "card_value":  (14, 16, 18, 22),
        "card_label":  ( 8,  9,  9, 10),
        "body":        (10, 11, 12, 14),
        "body_bold":   (11, 12, 13, 15),
        "label":       ( 9, 10, 10, 11),
        "entry":       (11, 12, 12, 14),
        "btn":         (10, 11, 12, 13),
        "nav":         (10, 11, 11, 12),
        "name":        (16, 18, 20, 26),
        "reg":         (10, 11, 11, 12),
        "notif_title": (11, 12, 13, 14),
        "notif_body":  (10, 11, 12, 13),
    }

    _MODE_IDX = {"tiny": 0, "mobile": 1, "tablet": 2, "desktop": 3}

    def __init__(self, parent, sidebar, content_area, has_sidebar=True):
        self.parent        = parent
        self.sidebar       = sidebar
        self.content_area  = content_area
        self.has_sidebar   = has_sidebar   # True = permanent sidebar on desktop

        self.mode             = None
        self.hamburger_btn    = None
        self.on_mode_change   = None
        self.on_any_resize    = None
        self.sidebar_visible  = False
        self.registered_grids = []

        self.grid_padx = 6
        self.grid_pady = 6
        self._resize_job = None

        # Bind to top-level root for reliable window resize sensing
        try:
            self.root = self.parent.winfo_toplevel()
            self.root.bind("<Configure>", self._on_configure, add="+")
        except Exception:
            self.parent.bind("<Configure>", self._on_configure)

        self.apply_layout()
        self.parent.after(80, self.apply_layout)

    # ── Resize debounce ───────────────────────────────────────────────
    def _on_configure(self, event):
        # Only detect resizes from the root window or the parent container itself
        if event.widget not in (self.parent, getattr(self, "root", None)):
            return
        if self._resize_job:
            self.parent.after_cancel(self._resize_job)
        self._resize_job = self.parent.after(100, self.apply_layout)

    # ── Core layout applier ───────────────────────────────────────────
    def apply_layout(self, force=False):
        try:
            if not (self.parent.winfo_exists() and
                    self.sidebar.winfo_exists() and
                    self.content_area.winfo_exists()):
                return

            self.parent.update_idletasks()
            width = self.parent.winfo_width()

            if width <= 1:
                new_mode = "mobile"
            elif width >= self.BP_DESKTOP:
                new_mode = "desktop"
            elif width >= self.BP_MOBILE:
                new_mode = "tablet"
            elif width >= self.BP_TINY:
                new_mode = "mobile"
            else:
                new_mode = "tiny"

            # ── Fluid grid refresh ──
            # We always refresh grids when the width changes, so they adapt instantly.
            self._refresh_all_grids(width)

            if new_mode == self.mode and not force:
                return

            self.mode = new_mode

            if new_mode == "desktop":
                self._apply_desktop()
            else:
                self._apply_small()

            if self.on_mode_change:
                self.on_mode_change()

            if self.on_any_resize:
                self.on_any_resize(width)

        except Exception as exc:
            print(f"[ResponsiveManager] apply_layout error: {exc}")

    # ── Desktop: permanent left sidebar ──────────────────────────────
    def _apply_desktop(self):
        """≥ 1000 px — sidebar fixed on the left, content fills right."""
        # Reset row weights
        self.parent.rowconfigure(0, weight=0)
        self.parent.rowconfigure(1, weight=1)

        if self.has_sidebar:
            sw = 200
            self.parent.columnconfigure(0, weight=0, minsize=sw)
            self.parent.columnconfigure(1, weight=1)
            self.sidebar.configure(width=sw, fg_color="#101214")
            self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
            self.content_area.grid(row=0, column=1, rowspan=2, sticky="nsew")
            self.sidebar_visible = True
        else:
            self.parent.columnconfigure(0, weight=1)
            self.parent.columnconfigure(1, weight=0, minsize=0)
            self.sidebar.grid_forget()
            self.content_area.grid(row=0, column=0, columnspan=2,
                                   rowspan=2, sticky="nsew")
            self.sidebar_visible = False



    # ── Small: dropdown hamburger menu ────────────────────────────────
    def _apply_small(self):
        """< 1000 px — sidebar is a toggled dropdown row above content."""
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=0, minsize=0)
        self.parent.rowconfigure(0, weight=0)   # dropdown row (row 0)
        self.parent.rowconfigure(1, weight=1)   # content (row 1)

        # Ensure sidebar is hidden (collapsed) initially
        self.sidebar.grid_forget()
        self.sidebar_visible = False

        # Content always in row 1
        self.content_area.grid(row=1, column=0, columnspan=2, sticky="nsew")



    # ── Sidebar toggle ─────────────────────────────────────────────────
    def toggle_sidebar(self):
        if self.mode == "desktop":
            return
        if self.sidebar_visible:
            self.hide_sidebar()
        else:
            self._open_sidebar()

    def _open_sidebar(self):
        h = {"tiny": 300, "mobile": 330, "tablet": 380}.get(self.mode, 330)
        self.sidebar.configure(height=h, fg_color="#1a1c1e")
        # Place sidebar in row 0, spanning full width
        self.sidebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.sidebar_visible = True

    def hide_sidebar(self):
        if self.mode != "desktop":
            self.sidebar.grid_forget()
            self.sidebar_visible = False

    # ── Font helpers ──────────────────────────────────────────────────
    def fs(self, key):
        row = self.FONT_TABLE.get(key)
        if not row:
            return 12
        return row[self._MODE_IDX.get(self.mode, 3)]

    def font(self, key, weight="normal", family="Segoe UI"):
        size = self.fs(key)
        if weight == "normal":
            return (family, size)
        return (family, size, weight)

    # ── Grid management ───────────────────────────────────────────────
    def register_grid(self, frame, max_cols):
        info = {"frame": frame, "max_cols": max_cols}
        self.registered_grids.append(info)
        self._update_grid_columns(info, self._cols_for_mode(max_cols))

    def _refresh_all_grids(self, width=None):
        alive = []
        for info in self.registered_grids:
            try:
                if info["frame"].winfo_exists():
                    # Calculate columns based on width if provided, else mode
                    cols = self._cols_for_width(width, info["max_cols"]) if width else self._cols_for_mode(info["max_cols"])
                    self._update_grid_columns(info, cols)
                    alive.append(info)
            except Exception:
                pass
        self.registered_grids = alive

    def _cols_for_width(self, width, max_cols):
        """More precise column calculation based on actual width."""
        if width < 450: return min(1, max_cols)
        if width < 750: return min(2, max_cols)
        if width < 1100: return min(3, max_cols)
        return max_cols

    def _cols_for_mode(self, max_cols):
        if self.mode == "tiny":
            return min(2, max_cols)
        if self.mode == "mobile":
            return min(2, max_cols)
        if self.mode == "tablet":
            return min(2, max_cols)
        return max_cols  # desktop

    def _update_grid_columns(self, grid_info, cols):
        frame = grid_info["frame"]
        if not frame.winfo_exists():
            return
        cols = max(1, cols)
        for i in range(12):
            frame.columnconfigure(
                i, weight=1 if i < cols else 0, minsize=0
            )
        for idx, child in enumerate(frame.winfo_children()):
            child.grid(
                row=idx // cols, column=idx % cols,
                padx=self.grid_padx, pady=self.grid_pady,
                sticky="nsew"
            )

    # ── Hamburger button factory ───────────────────────────────────────
    def create_hamburger_button(self, parent):
        self.hamburger_btn = ctk.CTkButton(
            parent,
            text="☰",
            width=44, height=44,
            font=("Segoe UI", 24, "bold"),
            fg_color="darkorange",
            text_color="black",
            hover_color="#e67e22",
            command=self.toggle_sidebar,
            cursor="hand2",
            corner_radius=12
        )

        return self.hamburger_btn



    # ── Convenience helpers ───────────────────────────────────────────
    def pad(self, tiny=8, mobile=10, tablet=14, desktop=20):
        return {
            "tiny": tiny, "mobile": mobile,
            "tablet": tablet, "desktop": desktop
        }.get(self.mode, desktop)

    def is_small(self):
        return self.mode in ("tiny", "mobile")

    def is_portrait(self):
        return self.mode != "desktop"


# ── Module-level helpers (backwards-compatible) ───────────────────────

def setup_dashboard_layout(parent):
    parent.columnconfigure(0, weight=0, minsize=200)
    parent.columnconfigure(1, weight=1)
    parent.rowconfigure(0, weight=1)
    return parent


def get_adaptive_columns(width, threshold=850, max_cols=4):
    if width < 400:       return 1
    if width < 600:       return 1
    if width < threshold: return 2
    return max_cols