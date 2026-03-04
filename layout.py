import customtkinter as ctk


class ResponsiveManager:
    """
    Manages the dashboard's two-column (sidebar + content) layout.
    Automatically switches between landscape (sidebar visible) and
    portrait (sidebar hidden, hamburger menu) when the window is resized.
    Also keeps track of registered grid frames so their column counts
    update whenever the layout mode changes.
    """

    # ------------------------------------------------------------------
    # __init__(parent, sidebar, content_area)
    # PURPOSE : Store references to the three main widgets, initialise
    #           state variables, and bind the <Configure> event so
    #           apply_layout() is called whenever the window resizes.
    # ------------------------------------------------------------------
    def __init__(self, parent, sidebar, content_area):
        self.parent       = parent
        self.sidebar      = sidebar
        self.content_area = content_area
        self.mode         = "landscape"  # OR portrait
        self.threshold    = 850

        # Grid registry for child components that need weight updates
        self.registered_grids = []

        self.sidebar_visible = True  # Track visibility

        # Bind resize event
        self.parent.bind("<Configure>", self._on_configure)
    # END __init__

    # ------------------------------------------------------------------
    # _on_configure(event)
    # PURPOSE : Event handler called on every window resize. Delegates
    #           to apply_layout() only when the main window fires the
    #           event (not child widgets).
    # ------------------------------------------------------------------
    def _on_configure(self, event):
        # Only handle if event is for the main parent window
        if event.widget == self.parent:
            self.apply_layout()
    # END _on_configure

    # ------------------------------------------------------------------
    # apply_layout()
    # PURPOSE : Check the current window width against the threshold
    #           and switch to portrait or landscape mode as needed.
    # ------------------------------------------------------------------
    def apply_layout(self):
        width = self.parent.winfo_width()

        if width < self.threshold and self.mode == "landscape":
            self._set_portrait_mode()
        elif width >= self.threshold and self.mode == "portrait":
            self._set_landscape_mode()
    # END apply_layout

    # ------------------------------------------------------------------
    # _set_portrait_mode()
    # PURPOSE : Switch to portrait/mobile layout: hide the sidebar,
    #           expand the content area to full width, and collapse
    #           all registered grid frames to a single column.
    # ------------------------------------------------------------------
    def _set_portrait_mode(self):
        self.mode = "portrait"
        # Reset grid weights
        self.parent.columnconfigure(0, weight=1, minsize=0)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=0)
        self.parent.rowconfigure(1, weight=1)

        # Hide sidebar by default in mobile/portrait
        self.sidebar.grid_forget()
        self.sidebar_visible = False

        # Content takes full width
        self.content_area.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Update registered grids (e.g. stats cards)
        for grid_info in self.registered_grids:
            self._update_grid_columns(grid_info, 1)
    # END _set_portrait_mode

    # ------------------------------------------------------------------
    # toggle_sidebar()
    # PURPOSE : Show or hide the sidebar when in portrait mode.
    #           Called by the hamburger (☰) button.
    # ------------------------------------------------------------------
    def toggle_sidebar(self):
        """Toggles sidebar visibility in portrait mode"""
        if self.mode == "portrait":
            if self.sidebar_visible:
                self.sidebar.grid_forget()
                self.sidebar_visible = False
            else:
                self.sidebar.grid(row=0, column=0, columnspan=2, sticky="ew")
                self.sidebar.configure(height=250)  # Give enough height for menu
                self.sidebar_visible = True
    # END toggle_sidebar

    # ------------------------------------------------------------------
    # _set_landscape_mode()
    # PURPOSE : Switch to the normal desktop layout: restore the sidebar
    #           column, reset content area to column 1, and restore all
    #           registered grids to their maximum column counts.
    # ------------------------------------------------------------------
    def _set_landscape_mode(self):
        self.mode = "landscape"
        self.parent.columnconfigure(0, weight=0, minsize=240)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=0)  # Reset row 1

        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.configure(width=240, height=0)  # Reset height
        self.content_area.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.sidebar_visible = True

        for grid_info in self.registered_grids:
            self._update_grid_columns(grid_info, grid_info["max_cols"])
    # END _set_landscape_mode

    # ------------------------------------------------------------------
    # register_grid(frame, max_cols)
    # PURPOSE : Register a grid frame so that its column count is
    #           automatically adjusted when the layout mode changes.
    #           Immediately applies the correct column count.
    # ------------------------------------------------------------------
    def register_grid(self, frame, max_cols):
        grid_info = {"frame": frame, "max_cols": max_cols}
        self.registered_grids.append(grid_info)
        # Apply current mode immediately
        cols = 1 if self.mode == "portrait" else max_cols
        self._update_grid_columns(grid_info, cols)
    # END register_grid

    # ------------------------------------------------------------------
    # _update_grid_columns(grid_info, cols)
    # PURPOSE : Re-pack all children of a registered frame into the
    #           given number of columns using grid geometry.
    # ------------------------------------------------------------------
    def _update_grid_columns(self, grid_info, cols):
        frame = grid_info["frame"]
        if not frame.winfo_exists():
            return

        # Configure columns
        for i in range(10):  # Clean up
            frame.columnconfigure(i, weight=0 if i >= cols else 1)

        # Reposition children if they were gridded
        children = frame.winfo_children()
        for i, child in enumerate(children):
            row = i // cols
            col = i % cols
            child.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
    # END _update_grid_columns

    # ------------------------------------------------------------------
    # create_hamburger_button(parent)
    # PURPOSE : Create and return a ☰ button that calls toggle_sidebar
    #           when clicked. Should be placed in portrait mode headers.
    # ------------------------------------------------------------------
    def create_hamburger_button(self, parent):
        return ctk.CTkButton(parent, text="☰", width=40, height=40,
                             font=("Arial", 24, "bold"), fg_color="transparent",
                             text_color="white", hover_color="#333333",
                             command=self.toggle_sidebar)
    # END create_hamburger_button


# ------------------------------------------------------------------
# setup_dashboard_layout(parent)
# PURPOSE : Apply the initial landscape grid configuration to the
#           root window (sidebar column fixed at 240px, content
#           column expands, single row fills height).
# RETURNS : parent (same object, for chaining)
# ------------------------------------------------------------------
def setup_dashboard_layout(parent):
    """Initial setup (Landscape by default)"""
    parent.columnconfigure(0, weight=0, minsize=240)
    parent.columnconfigure(1, weight=1)
    parent.rowconfigure(0, weight=1)
    return parent
# END setup_dashboard_layout


# ------------------------------------------------------------------
# get_adaptive_columns(width, threshold, max_cols)
# PURPOSE : Return the appropriate number of grid columns for a
#           given container width. Used by stat card grids.
# RETURNS : 1, 2, or max_cols depending on width breakpoints.
# ------------------------------------------------------------------
def get_adaptive_columns(width, threshold=850, max_cols=4):
    """Helper to return number of columns based on width"""
    if width < 500: return 1
    if width < threshold: return 2
    return max_cols
# END get_adaptive_columns
