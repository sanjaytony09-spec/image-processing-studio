"""
=============================================================================
IMAGE PROCESSING TOOLKIT
=============================================================================
A comprehensive, interactive desktop application for digital image processing,
filtering, geometric transformations, histogram visualization, and batch processing.

Built with: Python, OpenCV, Tkinter, Pillow, NumPy, and Matplotlib.
=============================================================================
"""

import os
import sys
from typing import Optional, List, Tuple, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

# Windows console encoding safeguard
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.image_io import (
    load_image,
    save_image,
    bgr_to_pil,
    resize_for_display,
    SUPPORTED_EXTENSIONS
)
from modules.image_processing import (
    apply_grayscale,
    apply_gaussian_blur,
    apply_median_blur,
    apply_bilateral_filter,
    apply_sharpen,
    apply_canny_edge,
    apply_sepia,
    apply_negative,
    apply_emboss,
    apply_cartoon,
    apply_histogram_equalization
)
from modules.image_transformations import (
    rotate_image,
    flip_image,
    resize_image,
    crop_image,
    adjust_brightness_contrast
)
from modules.histogram import generate_histogram_figure

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# =============================================================================
# THEME PALETTE CONSTANTS
# =============================================================================
THEME = {
    "bg_main": "#0f172a",       # Slate 900
    "bg_sidebar": "#1e293b",    # Slate 800
    "bg_card": "#1e293b",       # Card background
    "bg_card_inner": "#0f172a", # Workspace canvas background
    "bg_header": "#182234",     # Header background
    "bg_control": "#1e293b",    # Parameter control bar
    "border": "#334155",        # Slate 700 border
    "border_light": "#475569",  # Slate 600
    "primary": "#6366f1",       # Indigo 500
    "primary_hover": "#4f46e5", # Indigo 600
    "secondary": "#0ea5e9",     # Sky 500
    "secondary_hover": "#0284c7",
    "success": "#10b981",       # Emerald 500
    "warning": "#f59e0b",       # Amber 500
    "danger": "#ef4444",        # Red 500
    "text_primary": "#f8fafc",  # Slate 50
    "text_secondary": "#94a3b8",# Slate 400
    "text_muted": "#64748b",    # Slate 500
    "accent_btn": "#3b82f6",    # Blue 500
    "btn_bg": "#334155",        # Button default
    "btn_hover": "#475569"
}


# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================
class ImageProcessingToolkitApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Processing Toolkit")
        self.root.geometry("1380x880")
        self.root.minsize(1050, 700)
        self.root.configure(bg=THEME["bg_main"])

        # Load App Icon if available
        self._load_app_icon()

        # Image State
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None
        self.preview_temp_image: Optional[np.ndarray] = None
        self.image_metadata: Dict[str, Any] = {}
        self.current_operation_name: str = "None"

        # Undo / Redo Stacks (stores tuple of (image_array, operation_name))
        self.undo_stack: List[Tuple[np.ndarray, str]] = []
        self.redo_stack: List[Tuple[np.ndarray, str]] = []
        self.max_stack_size = 25

        # PhotoImage References (prevents Python GC)
        self.orig_photo: Optional[ImageTk.PhotoImage] = None
        self.proc_photo: Optional[ImageTk.PhotoImage] = None

        # Display scale tracking for cropping coordinates mapping
        self.proc_display_scale = 1.0
        self.proc_offset_x = 0
        self.proc_offset_y = 0

        # Interactive Cropping State
        self.crop_mode_active = False
        self.crop_start_x: Optional[int] = None
        self.crop_start_y: Optional[int] = None
        self.crop_rect_id: Optional[int] = None

        # Active parameter tool tracking
        self.active_tool: Optional[str] = None
        self.live_preview_var = tk.BooleanVar(value=True)

        # Build GUI Layout
        self._setup_styles()
        self._build_header()
        self._build_main_layout()
        self._build_status_bar()

        # Bind Global Events & Shortcuts
        self._bind_events()

        # Check for sample image and show welcome message
        self.set_status("Ready. Click 'Upload Image' or choose a sample to begin.", "info")
        self._update_action_buttons_state()

    # -------------------------------------------------------------------------
    # App Icon Setup
    # -------------------------------------------------------------------------
    def _load_app_icon(self):
        icon_path = os.path.join(BASE_DIR, "assets", "app_icon.png")
        if os.path.exists(icon_path):
            try:
                icon_img = ImageTk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, icon_img)
                self._app_icon_ref = icon_img  # Keep reference
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # UI Styling & Tkinter Themes
    # -------------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Configure Base Styles
        style.configure(".", background=THEME["bg_main"], foreground=THEME["text_primary"], font=("Segoe UI", 9))
        style.configure("TFrame", background=THEME["bg_main"])
        style.configure("Sidebar.TFrame", background=THEME["bg_sidebar"])
        style.configure("Card.TFrame", background=THEME["bg_card"])
        style.configure("Header.TFrame", background=THEME["bg_header"])

        # Label Styles
        style.configure("HeaderTitle.TLabel", background=THEME["bg_header"], foreground=THEME["text_primary"], font=("Segoe UI", 14, "bold"))
        style.configure("HeaderSub.TLabel", background=THEME["bg_header"], foreground=THEME["text_secondary"], font=("Segoe UI", 9))
        style.configure("Category.TLabel", background=THEME["bg_sidebar"], foreground=THEME["secondary"], font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", background=THEME["bg_header"], foreground=THEME["text_secondary"], font=("Segoe UI", 9))
        style.configure("StatusAccent.TLabel", background=THEME["bg_header"], foreground=THEME["success"], font=("Segoe UI", 9, "bold"))

        # Scrollbar
        style.configure("Vertical.TScrollbar", background=THEME["bg_sidebar"], troughcolor=THEME["bg_main"], bordercolor=THEME["border"], arrowcolor=THEME["text_secondary"])

    # -------------------------------------------------------------------------
    # Header Section
    # -------------------------------------------------------------------------
    def _build_header(self):
        self.header_frame = tk.Frame(self.root, bg=THEME["bg_header"], height=64, padx=16, pady=8, highlightbackground=THEME["border"], highlightthickness=1)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        # Title and Subtitle Block
        title_block = tk.Frame(self.header_frame, bg=THEME["bg_header"])
        title_block.pack(side=tk.LEFT, fill=tk.Y)

        title_lbl = tk.Label(
            title_block,
            text="✨ Image Processing Toolkit",
            bg=THEME["bg_header"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 14, "bold")
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            title_block,
            text="An interactive image processing and enhancement application",
            bg=THEME["bg_header"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9)
        )
        sub_lbl.pack(anchor="w")

        # Top Action Buttons
        actions_frame = tk.Frame(self.header_frame, bg=THEME["bg_header"])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_upload = self._create_header_btn(actions_frame, "📁 Upload Image", self.on_upload_image, bg=THEME["primary"])
        self.btn_upload.pack(side=tk.LEFT, padx=4)

        self.btn_save = self._create_header_btn(actions_frame, "💾 Save Image", self.on_save_image, bg=THEME["success"])
        self.btn_save.pack(side=tk.LEFT, padx=4)

        self.btn_reset = self._create_header_btn(actions_frame, "↺ Reset", self.on_reset_image, bg=THEME["danger"])
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        # Vertical separator
        sep = tk.Frame(actions_frame, width=1, bg=THEME["border"], height=28)
        sep.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        self.btn_undo = self._create_header_btn(actions_frame, "↶ Undo", self.on_undo, bg=THEME["btn_bg"])
        self.btn_undo.pack(side=tk.LEFT, padx=3)

        self.btn_redo = self._create_header_btn(actions_frame, "↷ Redo", self.on_redo, bg=THEME["btn_bg"])
        self.btn_redo.pack(side=tk.LEFT, padx=3)

        sep2 = tk.Frame(actions_frame, width=1, bg=THEME["border"], height=28)
        sep2.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        self.btn_sample = self._create_header_btn(actions_frame, "🖼 Sample Image", self.on_load_sample_menu, bg=THEME["secondary"])
        self.btn_sample.pack(side=tk.LEFT, padx=3)

    def _create_header_btn(self, parent, text, command, bg):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            activebackground=THEME["btn_hover"],
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=5,
            cursor="hand2",
            bd=0
        )
        return btn

    # -------------------------------------------------------------------------
    # Main Layout: Sidebar + Central Workspace
    # -------------------------------------------------------------------------
    def _build_main_layout(self):
        self.main_container = tk.Frame(self.root, bg=THEME["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_workspace()

    # -------------------------------------------------------------------------
    # Sidebar Section
    # -------------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar_width = 280
        self.sidebar_frame = tk.Frame(self.main_container, bg=THEME["bg_sidebar"], width=sidebar_width, highlightbackground=THEME["border"], highlightthickness=1)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # Scrollable area for tools
        canvas = tk.Canvas(self.sidebar_frame, bg=THEME["bg_sidebar"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", command=canvas.yview)
        self.sidebar_content = tk.Frame(canvas, bg=THEME["bg_sidebar"], padx=10, pady=10)

        self.sidebar_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=self.sidebar_content, anchor="nw", width=sidebar_width - 18)
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mousewheel scrolling in sidebar
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e) if self.root.winfo_containing(e.x_root, e.y_root) in (canvas, self.sidebar_content) else None)

        self.sidebar_buttons = []

        # --- Section 1: Color & Tone ---
        self._create_category_label("🎨 Color & Tone")
        self._add_tool_btn("Grayscale Filter", lambda: self.apply_instant_filter("Grayscale", apply_grayscale))
        self._add_tool_btn("Sepia Filter", lambda: self.apply_instant_filter("Sepia", apply_sepia))
        self._add_tool_btn("Negative Filter", lambda: self.apply_instant_filter("Negative", apply_negative))
        self._add_tool_btn("Brightness & Contrast", self.activate_brightness_contrast_tool)

        # --- Section 2: Smoothing & Noise ---
        self._create_category_label("🔬 Smoothing & Noise")
        self._add_tool_btn("Gaussian Blur", self.activate_gaussian_blur_tool)
        self._add_tool_btn("Median Blur", self.activate_median_blur_tool)
        self._add_tool_btn("Bilateral Filter", self.activate_bilateral_tool)

        # --- Section 3: Details & Edges ---
        self._create_category_label("⚡ Details & Effects")
        self._add_tool_btn("Sharpen Filter", self.activate_sharpen_tool)
        self._add_tool_btn("Canny Edge Detection", self.activate_canny_tool)
        self._add_tool_btn("Emboss Filter", self.activate_emboss_tool)
        self._add_tool_btn("Cartoon Effect", self.activate_cartoon_tool)
        self._add_tool_btn("Histogram Equalization", lambda: self.apply_instant_filter("Equalize Contrast", apply_histogram_equalization))

        # --- Section 4: Transformations ---
        self._create_category_label("🔄 Transformations")
        self._add_tool_btn("Rotate 90° Clockwise", lambda: self.apply_transform("Rotate 90°", rotate_image, 90))
        self._add_tool_btn("Rotate 180°", lambda: self.apply_transform("Rotate 180°", rotate_image, 180))
        self._add_tool_btn("Rotate 270°", lambda: self.apply_transform("Rotate 270°", rotate_image, 270))
        self._add_tool_btn("Flip Horizontally", lambda: self.apply_transform("Flip Horizontal", flip_image, 'horizontal'))
        self._add_tool_btn("Flip Vertically", lambda: self.apply_transform("Flip Vertical", flip_image, 'vertical'))
        self._add_tool_btn("Crop Image", self.activate_crop_tool)
        self._add_tool_btn("Resize Image", self.activate_resize_tool)

        # --- Section 5: Analysis & Batch ---
        self._create_category_label("📊 Advanced Tools")
        self._add_tool_btn("Image Histogram", self.open_histogram_dialog, highlight=True)
        self._add_tool_btn("Batch Processing", self.open_batch_dialog, highlight=True)

    def _create_category_label(self, title: str):
        lbl = tk.Label(
            self.sidebar_content,
            text=title,
            bg=THEME["bg_sidebar"],
            fg=THEME["secondary"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            pady=6
        )
        lbl.pack(fill=tk.X, pady=(10, 2))

    def _add_tool_btn(self, name: str, command, highlight: bool = False):
        bg_col = "#243247" if highlight else "#273549"
        btn = tk.Button(
            self.sidebar_content,
            text=name,
            command=command,
            bg=bg_col,
            fg=THEME["text_primary"],
            activebackground=THEME["primary"],
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            anchor="w",
            padx=12,
            pady=6,
            bd=0,
            cursor="hand2"
        )
        btn.pack(fill=tk.X, pady=2)

        # Hover effect
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=THEME["primary"])
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=bg_col)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        self.sidebar_buttons.append(btn)
        return btn

    # -------------------------------------------------------------------------
    # Central Workspace Section (Original vs Processed Side by Side)
    # -------------------------------------------------------------------------
    def _build_workspace(self):
        self.workspace_frame = tk.Frame(self.main_container, bg=THEME["bg_main"], padx=12, pady=10)
        self.workspace_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Control/Parameter Adjustment Bar (Contextual dynamic controls)
        self.control_panel = tk.Frame(self.workspace_frame, bg=THEME["bg_card"], padx=14, pady=8, highlightbackground=THEME["border"], highlightthickness=1)
        self.control_panel.pack(fill=tk.X, pady=(0, 10))

        # Control Panel Inner Container
        self.param_controls_container = tk.Frame(self.control_panel, bg=THEME["bg_card"])
        self.param_controls_container.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self._show_default_control_panel_message("Select an image filter or transformation tool from the sidebar to adjust parameters.")

        # Side by Side Previews Area
        self.previews_container = tk.Frame(self.workspace_frame, bg=THEME["bg_main"])
        self.previews_container.pack(fill=tk.BOTH, expand=True)

        # 1. Left Card: Original Image
        self.left_card = tk.Frame(self.previews_container, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        self.left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        left_header = tk.Frame(self.left_card, bg=THEME["bg_header"], height=36, padx=10, pady=6)
        left_header.pack(fill=tk.X)
        tk.Label(left_header, text="📷 Original Image", bg=THEME["bg_header"], fg=THEME["text_primary"], font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.lbl_orig_dims = tk.Label(left_header, text="No image loaded", bg=THEME["bg_header"], fg=THEME["text_muted"], font=("Segoe UI", 8))
        self.lbl_orig_dims.pack(side=tk.RIGHT)

        self.canvas_orig = tk.Canvas(self.left_card, bg=THEME["bg_card_inner"], highlightthickness=0)
        self.canvas_orig.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 2. Right Card: Processed Image
        self.right_card = tk.Frame(self.previews_container, bg=THEME["bg_card"], highlightbackground=THEME["border"], highlightthickness=1)
        self.right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        right_header = tk.Frame(self.right_card, bg=THEME["bg_header"], height=36, padx=10, pady=6)
        right_header.pack(fill=tk.X)
        tk.Label(right_header, text="✨ Processed Image", bg=THEME["bg_header"], fg=THEME["primary"], font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.lbl_proc_dims = tk.Label(right_header, text="Current: Original", bg=THEME["bg_header"], fg=THEME["text_muted"], font=("Segoe UI", 8))
        self.lbl_proc_dims.pack(side=tk.RIGHT)

        self.canvas_proc = tk.Canvas(self.right_card, bg=THEME["bg_card_inner"], highlightthickness=0)
        self.canvas_proc.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Bind canvas resize events to dynamically update thumbnails
        self.canvas_orig.bind("<Configure>", lambda e: self._refresh_previews_on_resize())
        self.canvas_proc.bind("<Configure>", lambda e: self._refresh_previews_on_resize())

        # Bind interactive mouse events on canvas_proc for cropping
        self.canvas_proc.bind("<ButtonPress-1>", self._on_canvas_crop_press)
        self.canvas_proc.bind("<B1-Motion>", self._on_canvas_crop_motion)
        self.canvas_proc.bind("<ButtonRelease-1>", self._on_canvas_crop_release)

    def _show_default_control_panel_message(self, message: str):
        for widget in self.param_controls_container.winfo_children():
            widget.destroy()

        info_frame = tk.Frame(self.param_controls_container, bg=THEME["bg_card"])
        info_frame.pack(fill=tk.X, pady=4)

        tk.Label(
            info_frame,
            text=f"⚙ {message}",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)

    # -------------------------------------------------------------------------
    # Status Bar Section
    # -------------------------------------------------------------------------
    def _build_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=THEME["bg_header"], height=28, padx=14, pady=4, highlightbackground=THEME["border"], highlightthickness=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_icon = tk.Label(self.status_bar, text="●", fg=THEME["secondary"], bg=THEME["bg_header"], font=("Segoe UI", 10))
        self.status_icon.pack(side=tk.LEFT, padx=(0, 4))

        self.status_label = tk.Label(self.status_bar, text="Ready", bg=THEME["bg_header"], fg=THEME["text_primary"], font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        # Right-hand metadata indicator
        self.meta_label = tk.Label(
            self.status_bar,
            text="No Image Loaded | 0 × 0 px | Ready",
            bg=THEME["bg_header"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8)
        )
        self.meta_label.pack(side=tk.RIGHT)

    def set_status(self, message: str, status_type: str = "normal"):
        color_map = {
            "normal": THEME["text_primary"],
            "success": THEME["success"],
            "warning": THEME["warning"],
            "danger": THEME["danger"],
            "info": THEME["secondary"]
        }
        self.status_label.config(text=message, fg=color_map.get(status_type, THEME["text_primary"]))
        self.status_icon.config(fg=color_map.get(status_type, THEME["secondary"]))

    def _update_meta_chip(self):
        if self.processed_image is not None and self.image_metadata:
            h, w = self.processed_image.shape[:2]
            c = self.processed_image.shape[2] if len(self.processed_image.shape) == 3 else 1
            fn = self.image_metadata.get("filename", "image")
            fmt = self.image_metadata.get("file_format", "IMG")
            size_str = self.image_metadata.get("file_size_str", "")
            op = self.current_operation_name
            self.meta_label.config(
                text=f"{fn} | {w}×{h} px | {c} Channels | {fmt} | {size_str} | Operation: {op}"
            )
            self.lbl_proc_dims.config(text=f"{w}×{h} px ({op})")
            orig_h, orig_w = self.original_image.shape[:2]
            self.lbl_orig_dims.config(text=f"{orig_w}×{orig_h} px")
        else:
            self.meta_label.config(text="No Image Loaded | Ready")
            self.lbl_proc_dims.config(text="Current: None")
            self.lbl_orig_dims.config(text="No image loaded")

    # -------------------------------------------------------------------------
    # Shortcuts & Global Events
    # -------------------------------------------------------------------------
    def _bind_events(self):
        self.root.bind("<Control-z>", lambda e: self.on_undo())
        self.root.bind("<Control-y>", lambda e: self.on_redo())
        self.root.bind("<Control-Shift-Z>", lambda e: self.on_redo())
        self.root.bind("<Control-o>", lambda e: self.on_upload_image())
        self.root.bind("<Control-s>", lambda e: self.on_save_image())

    def _update_action_buttons_state(self):
        has_img = self.original_image is not None
        can_undo = len(self.undo_stack) > 0
        can_redo = len(self.redo_stack) > 0

        # Enable/Disable top buttons
        self.btn_save.config(state=tk.NORMAL if has_img else tk.DISABLED)
        self.btn_reset.config(state=tk.NORMAL if has_img else tk.DISABLED)
        self.btn_undo.config(state=tk.NORMAL if can_undo else tk.DISABLED)
        self.btn_redo.config(state=tk.NORMAL if can_redo else tk.DISABLED)

        # Enable/Disable sidebar tool buttons
        for btn in self.sidebar_buttons:
            # Keep sample button and batch processing accessible
            if "Batch" in btn['text']:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.NORMAL if has_img else tk.DISABLED)

    # -------------------------------------------------------------------------
    # Image Upload & Display Logic
    # -------------------------------------------------------------------------
    def on_upload_image(self):
        file_types = [
            ("Supported Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif;*.webp"),
            ("JPEG Files", "*.jpg;*.jpeg"),
            ("PNG Files", "*.png"),
            ("BMP Files", "*.bmp"),
            ("TIFF Files", "*.tiff;*.tif"),
            ("WEBP Files", "*.webp"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Select an Image to Process",
            filetypes=file_types
        )
        if not file_path:
            return

        self._load_image_from_path(file_path)

    def on_load_sample_menu(self):
        samples_dir = os.path.join(BASE_DIR, "samples")
        if not os.path.exists(samples_dir):
            messagebox.showinfo("No Samples", "No sample images found in the samples/ folder.")
            return

        sample_files = [f for f in os.listdir(samples_dir) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        if not sample_files:
            messagebox.showinfo("No Samples", "No sample images found in the samples/ folder.")
            return

        # Popup menu to select sample
        menu = tk.Menu(self.root, tearoff=0, bg=THEME["bg_card"], fg=THEME["text_primary"], activebackground=THEME["primary"])
        for sfile in sample_files:
            full_path = os.path.join(samples_dir, sfile)
            menu.add_command(label=sfile, command=lambda p=full_path: self._load_image_from_path(p))

        # Show menu near sample button
        try:
            x = self.btn_sample.winfo_rootx()
            y = self.btn_sample.winfo_rooty() + self.btn_sample.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _load_image_from_path(self, file_path: str):
        try:
            img, metadata = load_image(file_path)
            self.original_image = img.copy()
            self.processed_image = img.copy()
            self.preview_temp_image = None
            self.image_metadata = metadata
            self.current_operation_name = "Original"

            # Reset Undo / Redo stacks
            self.undo_stack.clear()
            self.redo_stack.clear()

            self._update_action_buttons_state()
            self._update_meta_chip()
            self._render_images()
            self.set_status(f"Loaded '{metadata['filename']}' successfully ({metadata['width']}×{metadata['height']} px).", "success")
        except Exception as e:
            messagebox.showerror("Image Loading Error", f"Failed to load image:\n{e}")
            self.set_status(f"Error loading image: {e}", "danger")

    def _render_images(self, processed_override: Optional[np.ndarray] = None):
        """Render both original and processed previews inside their canvas containers."""
        if self.original_image is None:
            return

        # 1. Render Original Image Canvas
        cw_orig = self.canvas_orig.winfo_width()
        ch_orig = self.canvas_orig.winfo_height()
        if cw_orig > 10 and ch_orig > 10:
            try:
                photo_orig, w_o, h_o = resize_for_display(self.original_image, cw_orig - 10, ch_orig - 10)
                self.orig_photo = photo_orig
                self.canvas_orig.delete("all")
                # Center image in canvas
                ox = max(0, (cw_orig - w_o) // 2)
                oy = max(0, (ch_orig - h_o) // 2)
                self.canvas_orig.create_image(ox, oy, anchor="nw", image=self.orig_photo)
            except Exception as e:
                print(f"Error rendering original: {e}")

        # 2. Render Processed Image Canvas
        target_proc = processed_override if processed_override is not None else self.processed_image
        if target_proc is None:
            target_proc = self.original_image

        cw_proc = self.canvas_proc.winfo_width()
        ch_proc = self.canvas_proc.winfo_height()
        if cw_proc > 10 and ch_proc > 10:
            try:
                photo_proc, w_p, h_p = resize_for_display(target_proc, cw_proc - 10, ch_proc - 10)
                self.proc_photo = photo_proc
                self.canvas_proc.delete("all")
                px = max(0, (cw_proc - w_p) // 2)
                py = max(0, (ch_proc - h_p) // 2)
                self.canvas_proc.create_image(px, py, anchor="nw", image=self.proc_photo)

                # Track scale and offset for interactive crop tool mapping
                orig_h, orig_w = target_proc.shape[:2]
                self.proc_display_scale = orig_w / w_p
                self.proc_offset_x = px
                self.proc_offset_y = py
                self.proc_display_w = w_p
                self.proc_display_h = h_p
            except Exception as e:
                print(f"Error rendering processed image: {e}")

    def _refresh_previews_on_resize(self):
        """Called automatically when canvas containers resize."""
        if self.original_image is not None:
            self._render_images(self.preview_temp_image)

    # -------------------------------------------------------------------------
    # Save Image Logic
    # -------------------------------------------------------------------------
    def on_save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("No Image", "There is no processed image to save.")
            return

        initial_name = f"processed_{self.image_metadata.get('filename', 'output.png')}"
        file_types = [
            ("PNG Image (*.png)", "*.png"),
            ("JPEG Image (*.jpg;*.jpeg)", "*.jpg;*.jpeg"),
            ("BMP Image (*.bmp)", "*.bmp"),
            ("TIFF Image (*.tiff;*.tif)", "*.tiff;*.tif"),
            ("WEBP Image (*.webp)", "*.webp")
        ]

        save_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            initialfile=initial_name,
            filetypes=file_types
        )
        if not save_path:
            return

        try:
            saved_file = save_image(self.processed_image, save_path)
            self.set_status(f"Saved processed image successfully to '{os.path.basename(saved_file)}'.", "success")
            messagebox.showinfo("Image Saved", f"Image saved successfully to:\n{saved_file}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image:\n{e}")
            self.set_status(f"Failed to save image: {e}", "danger")

    # -------------------------------------------------------------------------
    # Reset Image Logic
    # -------------------------------------------------------------------------
    def on_reset_image(self):
        if self.original_image is None:
            return

        # Push state to undo stack before reset
        self._push_undo("Reset to Original")
        self.processed_image = self.original_image.copy()
        self.preview_temp_image = None
        self.current_operation_name = "Original"

        self._show_default_control_panel_message("Image restored to original state.")
        self._render_images()
        self._update_meta_chip()
        self.set_status("Image restored to original state.", "info")

    # -------------------------------------------------------------------------
    # Undo / Redo System
    # -------------------------------------------------------------------------
    def _push_undo(self, operation_name: str):
        if self.processed_image is None:
            return

        # Save copy of current state before applying new operation
        self.undo_stack.append((self.processed_image.copy(), self.current_operation_name))
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)

        # Clear redo stack when new operation is committed
        self.redo_stack.clear()
        self._update_action_buttons_state()

    def on_undo(self):
        if not self.undo_stack or self.processed_image is None:
            return

        # Push current state to redo stack
        self.redo_stack.append((self.processed_image.copy(), self.current_operation_name))

        # Pop from undo stack
        prev_img, prev_op = self.undo_stack.pop()
        self.processed_image = prev_img
        self.preview_temp_image = None
        self.current_operation_name = prev_op

        self._update_action_buttons_state()
        self._update_meta_chip()
        self._render_images()
        self.set_status(f"Undid action. Current state: '{prev_op}'.", "info")

    def on_redo(self):
        if not self.redo_stack:
            return

        # Push current state to undo stack
        self.undo_stack.append((self.processed_image.copy(), self.current_operation_name))

        # Pop from redo stack
        next_img, next_op = self.redo_stack.pop()
        self.processed_image = next_img
        self.preview_temp_image = None
        self.current_operation_name = next_op

        self._update_action_buttons_state()
        self._update_meta_chip()
        self._render_images()
        self.set_status(f"Redid action: '{next_op}'.", "info")

    # -------------------------------------------------------------------------
    # Generic Processing Helpers
    # -------------------------------------------------------------------------
    def apply_instant_filter(self, filter_name: str, filter_func):
        """Apply a filter that requires no user slider parameters immediately."""
        if self.processed_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        try:
            self._push_undo(filter_name)
            result = filter_func(self.processed_image)
            self.processed_image = result
            self.current_operation_name = filter_name

            self._show_default_control_panel_message(f"Applied '{filter_name}' filter.")
            self._render_images()
            self._update_meta_chip()
            self.set_status(f"Filter '{filter_name}' applied successfully.", "success")
        except Exception as e:
            messagebox.showerror("Filter Error", f"Error applying '{filter_name}':\n{e}")
            self.set_status(f"Error applying '{filter_name}': {e}", "danger")

    def apply_transform(self, op_name: str, transform_func, *args, **kwargs):
        """Apply geometric transformation immediately."""
        if self.processed_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        try:
            self._push_undo(op_name)
            result = transform_func(self.processed_image, *args, **kwargs)
            self.processed_image = result
            self.current_operation_name = op_name

            self._show_default_control_panel_message(f"Applied transformation: '{op_name}'.")
            self._render_images()
            self._update_meta_chip()
            self.set_status(f"Transformation '{op_name}' applied successfully.", "success")
        except Exception as e:
            messagebox.showerror("Transformation Error", f"Error in '{op_name}':\n{e}")
            self.set_status(f"Error applying '{op_name}': {e}", "danger")

    # -------------------------------------------------------------------------
    # Interactive Parameter Control Panel Helpers
    # -------------------------------------------------------------------------
    def _prepare_control_panel(self, tool_title: str):
        """Clear control panel and prepare headers and Apply/Cancel buttons."""
        self.crop_mode_active = False
        self.preview_temp_image = None
        for widget in self.param_controls_container.winfo_children():
            widget.destroy()

        header_lbl = tk.Label(
            self.param_controls_container,
            text=f"⚙ {tool_title}",
            bg=THEME["bg_card"],
            fg=THEME["secondary"],
            font=("Segoe UI", 10, "bold")
        )
        header_lbl.pack(side=tk.LEFT, padx=(0, 16))

        # Controls container
        controls_box = tk.Frame(self.param_controls_container, bg=THEME["bg_card"])
        controls_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return controls_box

    def _add_apply_cancel_buttons(self, apply_command, cancel_command=None):
        btn_box = tk.Frame(self.param_controls_container, bg=THEME["bg_card"])
        btn_box.pack(side=tk.RIGHT, padx=4)

        apply_btn = tk.Button(
            btn_box,
            text="✓ Apply",
            command=apply_command,
            bg=THEME["primary"],
            fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=3,
            cursor="hand2"
        )
        apply_btn.pack(side=tk.LEFT, padx=3)

        cancel_cmd = cancel_command if cancel_command else self._on_cancel_tool
        cancel_btn = tk.Button(
            btn_box,
            text="✕ Cancel",
            command=cancel_cmd,
            bg=THEME["btn_bg"],
            fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            padx=10,
            pady=3,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=3)

    def _on_cancel_tool(self):
        self.crop_mode_active = False
        self.preview_temp_image = None
        self._render_images()
        self._show_default_control_panel_message("Action cancelled.")
        self.set_status("Operation cancelled.", "info")

    # -------------------------------------------------------------------------
    # 1. Gaussian Blur Tool
    # -------------------------------------------------------------------------
    def activate_gaussian_blur_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Gaussian Blur")

        tk.Label(box, text="Blur Intensity (Kernel Size):", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 8))
        val_lbl = tk.Label(box, text="7 px", bg=THEME["bg_card"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold"), width=5)
        val_lbl.pack(side=tk.LEFT)

        slider = tk.Scale(
            box,
            from_=3,
            to=31,
            orient=tk.HORIZONTAL,
            resolution=2,  # Keep odd numbers
            showvalue=0,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            troughcolor=THEME["bg_main"],
            highlightthickness=0,
            length=180
        )
        slider.set(7)
        slider.pack(side=tk.LEFT, padx=8)

        def update_preview(val):
            k = int(float(val))
            if k % 2 == 0:
                k += 1
            val_lbl.config(text=f"{k} px")
            self.preview_temp_image = apply_gaussian_blur(self.processed_image, kernel_size=k)
            self._render_images(self.preview_temp_image)

        slider.config(command=update_preview)

        def commit():
            k = int(slider.get())
            if k % 2 == 0:
                k += 1
            self._push_undo(f"Gaussian Blur (k={k})")
            self.processed_image = apply_gaussian_blur(self.processed_image, kernel_size=k)
            self.preview_temp_image = None
            self.current_operation_name = f"Gaussian Blur ({k}px)"
            self._show_default_control_panel_message(f"Applied Gaussian Blur with kernel {k}px.")
            self._render_images()
            self._update_meta_chip()
            self.set_status(f"Gaussian Blur applied successfully (k={k}).", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview(slider.get())

    # -------------------------------------------------------------------------
    # 2. Median Blur Tool
    # -------------------------------------------------------------------------
    def activate_median_blur_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Median Blur")

        tk.Label(box, text="Noise Reduction Intensity:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 8))
        val_lbl = tk.Label(box, text="5 px", bg=THEME["bg_card"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold"), width=5)
        val_lbl.pack(side=tk.LEFT)

        slider = tk.Scale(
            box,
            from_=3,
            to=21,
            orient=tk.HORIZONTAL,
            resolution=2,
            showvalue=0,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            troughcolor=THEME["bg_main"],
            highlightthickness=0,
            length=160
        )
        slider.set(5)
        slider.pack(side=tk.LEFT, padx=8)

        def update_preview(val):
            k = int(float(val))
            if k % 2 == 0:
                k += 1
            val_lbl.config(text=f"{k} px")
            self.preview_temp_image = apply_median_blur(self.processed_image, kernel_size=k)
            self._render_images(self.preview_temp_image)

        slider.config(command=update_preview)

        def commit():
            k = int(slider.get())
            if k % 2 == 0:
                k += 1
            self._push_undo(f"Median Blur (k={k})")
            self.processed_image = apply_median_blur(self.processed_image, kernel_size=k)
            self.preview_temp_image = None
            self.current_operation_name = f"Median Blur ({k}px)"
            self._show_default_control_panel_message(f"Applied Median Blur with kernel {k}px.")
            self._render_images()
            self._update_meta_chip()
            self.set_status(f"Median Blur applied (k={k}).", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview(slider.get())

    # -------------------------------------------------------------------------
    # 3. Bilateral Filter Tool
    # -------------------------------------------------------------------------
    def activate_bilateral_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Bilateral Filter (Edge-Preserving)")

        tk.Label(box, text="Diameter:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 4))
        d_slider = tk.Scale(box, from_=3, to=15, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=90)
        d_slider.set(9)
        d_slider.pack(side=tk.LEFT, padx=4)

        tk.Label(box, text="Color Sigma:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(8, 4))
        sc_slider = tk.Scale(box, from_=10, to=150, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=100)
        sc_slider.set(75)
        sc_slider.pack(side=tk.LEFT, padx=4)

        def update_preview(*args):
            d = int(d_slider.get())
            sc = float(sc_slider.get())
            self.preview_temp_image = apply_bilateral_filter(self.processed_image, diameter=d, sigma_color=sc, sigma_space=sc)
            self._render_images(self.preview_temp_image)

        d_slider.config(command=lambda e: update_preview())
        sc_slider.config(command=lambda e: update_preview())

        def commit():
            d = int(d_slider.get())
            sc = float(sc_slider.get())
            self._push_undo("Bilateral Filter")
            self.processed_image = apply_bilateral_filter(self.processed_image, diameter=d, sigma_color=sc, sigma_space=sc)
            self.preview_temp_image = None
            self.current_operation_name = f"Bilateral (d={d})"
            self._show_default_control_panel_message("Bilateral Filter applied.")
            self._render_images()
            self._update_meta_chip()
            self.set_status("Bilateral Filter applied successfully.", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview()

    # -------------------------------------------------------------------------
    # 4. Sharpen Tool
    # -------------------------------------------------------------------------
    def activate_sharpen_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Sharpening Filter")

        tk.Label(box, text="Sharpen Strength:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 6))
        val_lbl = tk.Label(box, text="1.0x", bg=THEME["bg_card"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold"), width=5)
        val_lbl.pack(side=tk.LEFT)

        slider = tk.Scale(
            box,
            from_=0.2,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            showvalue=0,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            troughcolor=THEME["bg_main"],
            highlightthickness=0,
            length=160
        )
        slider.set(1.0)
        slider.pack(side=tk.LEFT, padx=8)

        def update_preview(val):
            s = float(val)
            val_lbl.config(text=f"{s:.1f}x")
            self.preview_temp_image = apply_sharpen(self.processed_image, strength=s)
            self._render_images(self.preview_temp_image)

        slider.config(command=update_preview)

        def commit():
            s = float(slider.get())
            self._push_undo(f"Sharpen ({s:.1f}x)")
            self.processed_image = apply_sharpen(self.processed_image, strength=s)
            self.preview_temp_image = None
            self.current_operation_name = f"Sharpen ({s:.1f}x)"
            self._show_default_control_panel_message(f"Sharpening filter applied with strength {s:.1f}x.")
            self._render_images()
            self._update_meta_chip()
            self.set_status(f"Image sharpened ({s:.1f}x).", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview(slider.get())

    # -------------------------------------------------------------------------
    # 5. Canny Edge Detection Tool
    # -------------------------------------------------------------------------
    def activate_canny_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Canny Edge Detection")

        tk.Label(box, text="Low Threshold:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 4))
        low_slider = tk.Scale(box, from_=10, to=250, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=110)
        low_slider.set(50)
        low_slider.pack(side=tk.LEFT, padx=4)

        tk.Label(box, text="High Threshold:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(8, 4))
        high_slider = tk.Scale(box, from_=20, to=255, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=110)
        high_slider.set(150)
        high_slider.pack(side=tk.LEFT, padx=4)

        def update_preview(*args):
            l = int(low_slider.get())
            h = int(high_slider.get())
            self.preview_temp_image = apply_canny_edge(self.processed_image, low_thresh=l, high_thresh=h)
            self._render_images(self.preview_temp_image)

        low_slider.config(command=lambda e: update_preview())
        high_slider.config(command=lambda e: update_preview())

        def commit():
            l = int(low_slider.get())
            h = int(high_slider.get())
            self._push_undo("Canny Edge")
            self.processed_image = apply_canny_edge(self.processed_image, low_thresh=l, high_thresh=h)
            self.preview_temp_image = None
            self.current_operation_name = f"Canny ({l}-{h})"
            self._show_default_control_panel_message("Canny Edge Detection applied.")
            self._render_images()
            self._update_meta_chip()
            self.set_status("Canny Edge Detection applied.", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview()

    # -------------------------------------------------------------------------
    # 6. Brightness and Contrast Tool
    # -------------------------------------------------------------------------
    def activate_brightness_contrast_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Brightness & Contrast")

        tk.Label(box, text="Brightness:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 4))
        b_slider = tk.Scale(box, from_=-100, to=100, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=120)
        b_slider.set(0)
        b_slider.pack(side=tk.LEFT, padx=4)

        tk.Label(box, text="Contrast:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(8, 4))
        c_slider = tk.Scale(box, from_=-100, to=100, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=120)
        c_slider.set(0)
        c_slider.pack(side=tk.LEFT, padx=4)

        def update_preview(*args):
            b = float(b_slider.get())
            c = float(c_slider.get())
            self.preview_temp_image = adjust_brightness_contrast(self.processed_image, brightness=b, contrast=c)
            self._render_images(self.preview_temp_image)

        b_slider.config(command=lambda e: update_preview())
        c_slider.config(command=lambda e: update_preview())

        def commit():
            b = float(b_slider.get())
            c = float(c_slider.get())
            self._push_undo("Brightness/Contrast")
            self.processed_image = adjust_brightness_contrast(self.processed_image, brightness=b, contrast=c)
            self.preview_temp_image = None
            self.current_operation_name = f"B/C (B:{int(b)}, C:{int(c)})"
            self._show_default_control_panel_message("Brightness & Contrast adjustments applied.")
            self._render_images()
            self._update_meta_chip()
            self.set_status("Brightness & Contrast updated.", "success")

        self._add_apply_cancel_buttons(commit)

    # -------------------------------------------------------------------------
    # 7. Emboss Filter Tool
    # -------------------------------------------------------------------------
    def activate_emboss_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Emboss Filter")

        tk.Label(box, text="3D Relief Intensity:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 6))
        slider = tk.Scale(box, from_=0.5, to=2.5, resolution=0.1, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=140)
        slider.set(1.0)
        slider.pack(side=tk.LEFT, padx=6)

        def update_preview(val):
            intens = float(val)
            self.preview_temp_image = apply_emboss(self.processed_image, intensity=intens)
            self._render_images(self.preview_temp_image)

        slider.config(command=update_preview)

        def commit():
            intens = float(slider.get())
            self._push_undo("Emboss Filter")
            self.processed_image = apply_emboss(self.processed_image, intensity=intens)
            self.preview_temp_image = None
            self.current_operation_name = f"Emboss ({intens:.1f})"
            self._show_default_control_panel_message("Emboss filter applied.")
            self._render_images()
            self._update_meta_chip()
            self.set_status("Emboss effect applied.", "success")

        self._add_apply_cancel_buttons(commit)
        update_preview(slider.get())

    # -------------------------------------------------------------------------
    # 8. Cartoon Effect Tool
    # -------------------------------------------------------------------------
    def activate_cartoon_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Cartoon Effect")

        tk.Label(box, text="Stylization Passes:", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 4))
        p_slider = tk.Scale(box, from_=2, to=8, orient=tk.HORIZONTAL, showvalue=1, bg=THEME["bg_card"], fg=THEME["text_primary"], troughcolor=THEME["bg_main"], highlightthickness=0, length=100)
        p_slider.set(5)
        p_slider.pack(side=tk.LEFT, padx=4)

        def commit():
            passes = int(p_slider.get())
            self.set_status("Rendering Cartoon Effect (smoothing + sketch edge extraction)...", "info")
            self.root.update_idletasks()
            self._push_undo("Cartoon Effect")
            self.processed_image = apply_cartoon(self.processed_image, bilateral_passes=passes)
            self.preview_temp_image = None
            self.current_operation_name = f"Cartoon ({passes} passes)"
            self._show_default_control_panel_message("Cartoon effect applied.")
            self._render_images()
            self._update_meta_chip()
            self.set_status("Cartoon effect applied successfully.", "success")

        self._add_apply_cancel_buttons(commit)

    # -------------------------------------------------------------------------
    # 9. Resize Image Tool
    # -------------------------------------------------------------------------
    def activate_resize_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Resize Image")

        cur_h, cur_w = self.processed_image.shape[:2]
        aspect_ratio = cur_w / cur_h

        tk.Label(box, text="Width (px):", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(0, 4))
        w_entry = tk.Entry(box, width=7, bg=THEME["bg_main"], fg=THEME["text_primary"], insertbackground="white", bd=1)
        w_entry.insert(0, str(cur_w))
        w_entry.pack(side=tk.LEFT, padx=4)

        tk.Label(box, text="Height (px):", bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side=tk.LEFT, padx=(8, 4))
        h_entry = tk.Entry(box, width=7, bg=THEME["bg_main"], fg=THEME["text_primary"], insertbackground="white", bd=1)
        h_entry.insert(0, str(cur_h))
        h_entry.pack(side=tk.LEFT, padx=4)

        keep_ratio_var = tk.BooleanVar(value=True)
        cb_ratio = tk.Checkbutton(
            box,
            text="Maintain Aspect Ratio",
            variable=keep_ratio_var,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            selectcolor=THEME["bg_main"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["text_primary"]
        )
        cb_ratio.pack(side=tk.LEFT, padx=10)

        # Quick preset buttons (50%, 75%, 150%, 200%)
        preset_frame = tk.Frame(box, bg=THEME["bg_card"])
        preset_frame.pack(side=tk.LEFT, padx=8)

        def set_scale(scale_factor):
            nw = max(1, int(cur_w * scale_factor))
            nh = max(1, int(cur_h * scale_factor))
            w_entry.delete(0, tk.END)
            w_entry.insert(0, str(nw))
            h_entry.delete(0, tk.END)
            h_entry.insert(0, str(nh))

        for factor, lbl in [(0.5, "50%"), (0.75, "75%"), (1.5, "150%"), (2.0, "200%")]:
            b = tk.Button(preset_frame, text=lbl, command=lambda f=factor: set_scale(f), bg=THEME["btn_bg"], fg="white", font=("Segoe UI", 7), padx=4, pady=1, relief=tk.FLAT)
            b.pack(side=tk.LEFT, padx=2)

        def on_w_change(*args):
            if keep_ratio_var.get():
                try:
                    val = int(w_entry.get())
                    new_h = max(1, int(round(val / aspect_ratio)))
                    h_entry.delete(0, tk.END)
                    h_entry.insert(0, str(new_h))
                except Exception:
                    pass

        w_entry.bind("<KeyRelease>", on_w_change)

        def commit():
            try:
                new_w = int(w_entry.get())
                new_h = int(h_entry.get())
                if new_w <= 0 or new_h <= 0:
                    raise ValueError("Dimensions must be positive integers.")
                if new_w > 8000 or new_h > 8000:
                    raise ValueError("Dimensions exceed maximum allowed limit of 8000 pixels.")

                self._push_undo(f"Resize ({new_w}×{new_h})")
                self.processed_image = resize_image(self.processed_image, new_w, new_h)
                self.preview_temp_image = None
                self.current_operation_name = f"Resized ({new_w}×{new_h})"
                self._show_default_control_panel_message(f"Image resized to {new_w}×{new_h} px.")
                self._render_images()
                self._update_meta_chip()
                self.set_status(f"Image resized to {new_w}×{new_h} px.", "success")
            except Exception as e:
                messagebox.showerror("Resize Error", f"Invalid resize parameters:\n{e}")

        self._add_apply_cancel_buttons(commit)

    # -------------------------------------------------------------------------
    # 10. Interactive Crop Tool
    # -------------------------------------------------------------------------
    def activate_crop_tool(self):
        if self.processed_image is None:
            return
        box = self._prepare_control_panel("Crop Tool (Interactive Drag)")

        self.crop_mode_active = True
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_coords = None

        tk.Label(
            box,
            text="👉 Click and drag on the Processed Image to select crop region.",
            bg=THEME["bg_card"],
            fg=THEME["warning"],
            font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT, padx=6)

        self.lbl_crop_info = tk.Label(
            box,
            text="Selected: None",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9)
        )
        self.lbl_crop_info.pack(side=tk.LEFT, padx=10)

        def commit():
            if not self.crop_coords:
                messagebox.showwarning("No Selection", "Please click and drag a rectangular region on the processed image first.")
                return

            x1, y1, x2, y2 = self.crop_coords
            try:
                self._push_undo(f"Crop ({x2-x1}×{y2-y1})")
                self.processed_image = crop_image(self.processed_image, x1, y1, x2, y2)
                self.preview_temp_image = None
                self.current_operation_name = f"Cropped ({x2-x1}×{y2-y1})"
                self.crop_mode_active = False
                self._show_default_control_panel_message("Crop applied successfully.")
                self._render_images()
                self._update_meta_chip()
                self.set_status(f"Image cropped to ({x2-x1}×{y2-y1}) px.", "success")
            except Exception as e:
                messagebox.showerror("Crop Error", f"Failed to crop image:\n{e}")

        def cancel():
            self.crop_mode_active = False
            self.canvas_proc.delete("crop_rect")
            self._on_cancel_tool()

        self._add_apply_cancel_buttons(commit, cancel)

    def _on_canvas_crop_press(self, event):
        if not self.crop_mode_active or self.processed_image is None:
            return
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.canvas_proc.delete("crop_rect")

    def _on_canvas_crop_motion(self, event):
        if not self.crop_mode_active or self.crop_start_x is None:
            return
        cur_x, cur_y = event.x, event.y
        self.canvas_proc.delete("crop_rect")
        # Draw translucent dashed rectangle
        self.canvas_proc.create_rectangle(
            self.crop_start_x, self.crop_start_y, cur_x, cur_y,
            outline="#f59e0b",
            width=2,
            dash=(4, 4),
            tags="crop_rect"
        )

    def _on_canvas_crop_release(self, event):
        if not self.crop_mode_active or self.crop_start_x is None:
            return
        end_x, end_y = event.x, event.y

        # Convert canvas screen coordinates to full-resolution image coordinates
        scale = getattr(self, 'proc_display_scale', 1.0)
        off_x = getattr(self, 'proc_offset_x', 0)
        off_y = getattr(self, 'proc_offset_y', 0)

        img_h, img_w = self.processed_image.shape[:2]

        x1_screen = min(self.crop_start_x, end_x) - off_x
        x2_screen = max(self.crop_start_x, end_x) - off_x
        y1_screen = min(self.crop_start_y, end_y) - off_y
        y2_screen = max(self.crop_start_y, end_y) - off_y

        img_x1 = max(0, min(img_w, int(x1_screen * scale)))
        img_x2 = max(0, min(img_w, int(x2_screen * scale)))
        img_y1 = max(0, min(img_h, int(y1_screen * scale)))
        img_y2 = max(0, min(img_h, int(y2_screen * scale)))

        cw = img_x2 - img_x1
        ch = img_y2 - img_y1

        if cw > 5 and ch > 5:
            self.crop_coords = (img_x1, img_y1, img_x2, img_y2)
            if hasattr(self, 'lbl_crop_info'):
                self.lbl_crop_info.config(text=f"Selection: {cw}×{ch} px at ({img_x1}, {img_y1})")
        else:
            self.crop_coords = None
            if hasattr(self, 'lbl_crop_info'):
                self.lbl_crop_info.config(text="Selection too small")

    # -------------------------------------------------------------------------
    # 11. Histogram Window
    # -------------------------------------------------------------------------
    def open_histogram_dialog(self):
        if self.processed_image is None:
            messagebox.showwarning("No Image", "Please upload an image first to visualize its histogram.")
            return

        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Missing Dependency", "Matplotlib is required for histogram visualization.")
            return

        hist_win = tk.Toplevel(self.root)
        hist_win.title("Image Intensity Histogram - Image Processing Toolkit")
        hist_win.geometry("760x520")
        hist_win.minsize(620, 440)
        hist_win.configure(bg=THEME["bg_main"])
        hist_win.transient(self.root)

        # Header
        top_bar = tk.Frame(hist_win, bg=THEME["bg_header"], padx=14, pady=10)
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text="📊 Pixel Intensity Distribution Analysis",
            bg=THEME["bg_header"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT)

        # Mode Selection
        mode_frame = tk.Frame(top_bar, bg=THEME["bg_header"])
        mode_frame.pack(side=tk.RIGHT)

        mode_var = tk.StringVar(value="color")

        canvas_area = tk.Frame(hist_win, bg=THEME["bg_main"])
        canvas_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        current_canvas = [None]

        def render_hist():
            if current_canvas[0] is not None:
                current_canvas[0].get_tk_widget().destroy()

            fig = generate_histogram_figure(
                self.processed_image,
                mode=mode_var.get(),
                bg_color="#182234",
                text_color="#e0e6ed",
                grid_color="#2d3748"
            )
            canvas = FigureCanvasTkAgg(fig, master=canvas_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            current_canvas[0] = canvas

        rb_color = tk.Radiobutton(
            mode_frame,
            text="RGB Color Channels",
            variable=mode_var,
            value="color",
            command=render_hist,
            bg=THEME["bg_header"],
            fg=THEME["text_primary"],
            selectcolor=THEME["bg_main"],
            activebackground=THEME["bg_header"],
            activeforeground=THEME["text_primary"]
        )
        rb_color.pack(side=tk.LEFT, padx=6)

        rb_gray = tk.Radiobutton(
            mode_frame,
            text="Grayscale Intensity",
            variable=mode_var,
            value="gray",
            command=render_hist,
            bg=THEME["bg_header"],
            fg=THEME["text_primary"],
            selectcolor=THEME["bg_main"],
            activebackground=THEME["bg_header"],
            activeforeground=THEME["text_primary"]
        )
        rb_gray.pack(side=tk.LEFT, padx=6)

        render_hist()

    # -------------------------------------------------------------------------
    # 12. Batch Processing Window
    # -------------------------------------------------------------------------
    def open_batch_dialog(self):
        batch_win = tk.Toplevel(self.root)
        batch_win.title("Batch Image Processing - Image Processing Toolkit")
        batch_win.geometry("640x520")
        batch_win.minsize(560, 440)
        batch_win.configure(bg=THEME["bg_main"])
        batch_win.transient(self.root)

        # Header
        top_bar = tk.Frame(batch_win, bg=THEME["bg_header"], padx=14, pady=12)
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text="⚡ Batch Image Filter Pipeline",
            bg=THEME["bg_header"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            top_bar,
            text="Select multiple images, choose a filter, and process all in bulk.",
            bg=THEME["bg_header"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        body = tk.Frame(batch_win, bg=THEME["bg_main"], padx=16, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        selected_files: List[str] = []
        out_dir = [os.path.join(BASE_DIR, "output")]

        # Step 1: Input Images
        s1_frame = tk.Frame(body, bg=THEME["bg_main"])
        s1_frame.pack(fill=tk.X, pady=6)
        tk.Label(s1_frame, text="1. Select Input Images:", bg=THEME["bg_main"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold")).pack(anchor="w")

        f_status_lbl = tk.Label(s1_frame, text="No images selected (0 files)", bg=THEME["bg_main"], fg=THEME["text_muted"])
        f_status_lbl.pack(side=tk.LEFT, pady=4)

        def pick_files():
            files = filedialog.askopenfilenames(
                title="Select Images to Process",
                filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.webp"), ("All Files", "*.*")]
            )
            if files:
                selected_files.clear()
                selected_files.extend(files)
                f_status_lbl.config(text=f"Selected {len(selected_files)} images", fg=THEME["success"])

        btn_pick_files = tk.Button(s1_frame, text="Browse Files...", command=pick_files, bg=THEME["primary"], fg="white", relief=tk.FLAT, padx=10, pady=2, cursor="hand2")
        btn_pick_files.pack(side=tk.RIGHT)

        # Step 2: Choose Filter
        s2_frame = tk.Frame(body, bg=THEME["bg_main"])
        s2_frame.pack(fill=tk.X, pady=10)
        tk.Label(s2_frame, text="2. Choose Processing Operation:", bg=THEME["bg_main"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold")).pack(anchor="w")

        filter_options = [
            "Grayscale Filter",
            "Gaussian Blur (k=7)",
            "Median Blur (k=5)",
            "Sharpen Filter",
            "Canny Edge Detection",
            "Sepia Filter",
            "Negative Filter",
            "Emboss Filter",
            "Cartoon Effect",
            "Histogram Equalization (CLAHE)"
        ]
        chosen_filter_var = tk.StringVar(value=filter_options[0])
        opt_menu = ttk.Combobox(s2_frame, textvariable=chosen_filter_var, values=filter_options, state="readonly", width=35)
        opt_menu.pack(anchor="w", pady=4)

        # Step 3: Destination Folder
        s3_frame = tk.Frame(body, bg=THEME["bg_main"])
        s3_frame.pack(fill=tk.X, pady=6)
        tk.Label(s3_frame, text="3. Destination Output Folder:", bg=THEME["bg_main"], fg=THEME["secondary"], font=("Segoe UI", 9, "bold")).pack(anchor="w")

        dir_lbl = tk.Label(s3_frame, text=f"Output: {out_dir[0]}", bg=THEME["bg_main"], fg=THEME["text_secondary"], font=("Segoe UI", 8))
        dir_lbl.pack(side=tk.LEFT, pady=4)

        def pick_dir():
            d = filedialog.askdirectory(title="Select Destination Folder", initialdir=out_dir[0])
            if d:
                out_dir[0] = d
                dir_lbl.config(text=f"Output: {d}")

        btn_pick_dir = tk.Button(s3_frame, text="Change Folder...", command=pick_dir, bg=THEME["btn_bg"], fg="white", relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        btn_pick_dir.pack(side=tk.RIGHT)

        # Step 4: Progress and Logs
        progress_var = tk.DoubleVar(value=0.0)
        p_bar = ttk.Progressbar(body, variable=progress_var, maximum=100)
        p_bar.pack(fill=tk.X, pady=(12, 6))

        log_box = tk.Text(body, height=6, bg="#111827", fg="#9ca3af", font=("Consolas", 8), bd=1, relief=tk.SOLID)
        log_box.pack(fill=tk.BOTH, expand=True)

        def log_msg(msg: str):
            log_box.insert(tk.END, msg + "\n")
            log_box.see(tk.END)
            batch_win.update_idletasks()

        # Step 5: Run Batch Processing
        def run_batch():
            if not selected_files:
                messagebox.showwarning("No Files", "Please select one or more image files to process.")
                return

            os.makedirs(out_dir[0], exist_ok=True)
            filt = chosen_filter_var.get()
            log_box.delete("1.0", tk.END)
            log_msg(f"Starting batch processing of {len(selected_files)} images with '{filt}'...")

            total = len(selected_files)
            success_count = 0

            for idx, fpath in enumerate(selected_files):
                try:
                    img, _ = load_image(fpath)
                    if filt == "Grayscale Filter":
                        res = apply_grayscale(img)
                    elif "Gaussian" in filt:
                        res = apply_gaussian_blur(img, 7)
                    elif "Median" in filt:
                        res = apply_median_blur(img, 5)
                    elif "Sharpen" in filt:
                        res = apply_sharpen(img, 1.2)
                    elif "Canny" in filt:
                        res = apply_canny_edge(img, 50, 150)
                    elif "Sepia" in filt:
                        res = apply_sepia(img)
                    elif "Negative" in filt:
                        res = apply_negative(img)
                    elif "Emboss" in filt:
                        res = apply_emboss(img)
                    elif "Cartoon" in filt:
                        res = apply_cartoon(img, bilateral_passes=3)
                    elif "Equalization" in filt:
                        res = apply_histogram_equalization(img)
                    else:
                        res = img

                    bname = os.path.basename(fpath)
                    dest_file = os.path.join(out_dir[0], f"batch_{bname}")
                    save_image(res, dest_file)
                    success_count += 1
                    log_msg(f"[{idx+1}/{total}] Successfully processed {bname}")
                except Exception as ex:
                    log_msg(f"[{idx+1}/{total}] FAILED {os.path.basename(fpath)}: {ex}")

                progress_var.set(((idx + 1) / total) * 100)

            log_msg(f"\nDone! Successfully processed {success_count} / {total} files.")
            messagebox.showinfo("Batch Complete", f"Batch processing finished!\nProcessed {success_count} / {total} images.\nSaved into: {out_dir[0]}")

        run_btn = tk.Button(
            body,
            text="🚀 Start Batch Processing",
            command=run_batch,
            bg=THEME["success"],
            fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            pady=6,
            cursor="hand2"
        )
        run_btn.pack(fill=tk.X, pady=(8, 0))


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
def main():
    root = tk.Tk()
    app = ImageProcessingToolkitApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
