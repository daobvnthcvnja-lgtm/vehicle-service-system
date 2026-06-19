import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk, ImageFilter

# Theme Colors
COLOR_PRIMARY_DARK = "#4F6457"
COLOR_ACCENT_LIGHT = "#ACD0C0"
COLOR_ACTIVE_HOVER = "#75B1A9"
COLOR_ACCENT_GOLD = "#D9B44A"
COLOR_HEADER_BG = "#91C1B5"  # Blend of ACD0C0 and 75B1A9
COLOR_BG_LIGHT = "#F5F7F6"
COLOR_WHITE = "#FFFFFF"
COLOR_RED = "#D32F2F"  # Outlined default red

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def draw_gradient_canvas(canvas, width, height, color1, color2):
    canvas.delete("gradient_bg")
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    # Draw vertical gradient line by line
    for y in range(height):
        # Interpolate
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, width, y, fill=color, tags="gradient_bg")
    canvas.tag_lower("gradient_bg")

def generate_logo_icon(size=(64, 64)):
    import os
    # Try to load custom logo and process it
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust path to find logo in parent directory if it's placed there
    processed_path = os.path.join(base_dir, "logo_processed.png")
    raw_path = os.path.join(base_dir, "logo.png")
    
    # Fallback to check parent directory (the root)
    if not os.path.exists(raw_path):
        parent_dir = os.path.dirname(base_dir)
        processed_path = os.path.join(parent_dir, "logo_processed.png")
        raw_path = os.path.join(parent_dir, "logo.png")
    
    img = None
    if os.path.exists(processed_path):
        try:
            img = Image.open(processed_path)
        except Exception:
            pass
            
    if img is None and os.path.exists(raw_path):
        try:
            # Process on the fly: convert near-black pixels to transparent
            raw_img = Image.open(raw_path).convert("RGBA")
            width, height = raw_img.size
            pixels = raw_img.load()
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    val = max(r, g, b)
                    if val < 20:
                        new_a = 0
                    else:
                        new_a = min(255, int(val * 1.2))
                    pixels[x, y] = (r, g, b, new_a)
            raw_img.save(processed_path, "PNG")
            img = raw_img
        except Exception as e:
            print("Error processing logo image:", e)
            
    if img is not None:
        try:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized)
        except Exception as e:
            print("Error loading/resizing image:", e)
            
    # Procedural fallback
    base_img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    gold_color = (217, 180, 74, 255)  # #D9B44A
    cx, cy = 64, 64
    draw.ellipse([cx-40, cy-40, cx+40, cy+40], outline=gold_color, width=4)
    draw.ellipse([cx-20, cy-20, cx+20, cy+20], outline=gold_color, width=4)
    import math
    for i in range(8):
        angle = i * (math.pi / 4)
        x1 = cx + 38 * math.cos(angle)
        y1 = cy + 38 * math.sin(angle)
        x2 = cx + 48 * math.cos(angle)
        y2 = cy + 48 * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill=gold_color, width=6)
        
    draw.line([25, 103, 103, 25], fill=gold_color, width=6)
    draw.ellipse([93, 15, 113, 35], outline=gold_color, width=4)
    draw.ellipse([98, 20, 108, 30], fill=(0,0,0,0), outline=gold_color, width=2)
    draw.polygon([(93,25), (103,15), (113,25)], fill=(0,0,0,0))
    
    draw.line([20, 90, 45, 100], fill=gold_color, width=4)
    draw.line([45, 100, 80, 85], fill=gold_color, width=4)
    draw.ellipse([42, 97, 48, 103], fill=gold_color)
    draw.ellipse([77, 82, 83, 88], fill=gold_color)
    
    glow_img = base_img.filter(ImageFilter.GaussianBlur(5))
    composite = Image.new("RGBA", (128, 128), (0,0,0,0))
    composite.alpha_composite(glow_img)
    composite.alpha_composite(base_img)
    
    final_img = composite.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(final_img)

def generate_logout_icon():
    # Size 20x20, default red outline, logout door and arrow
    img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    red_color = (211, 47, 47, 255)  # Outlined red
    
    # Open door frame (lines from bottom left, up, right, down to bottom right)
    draw.line([(10, 36), (10, 4), (30, 4), (30, 36), (10, 36)], fill=red_color, width=3)
    
    # Arrow pushing outwards (left-to-right arrow)
    draw.line([(2, 20), (24, 20)], fill=red_color, width=3)
    draw.line([(16, 12), (24, 20), (16, 28)], fill=red_color, width=3)
    
    # Clear the center doorway a bit to show exit
    draw.rectangle([8, 12, 12, 28], fill=(0,0,0,0))
    
    final_img = img.resize((20, 20), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(final_img)

class CustomEntry(tk.Frame):
    def __init__(self, parent, placeholder="", is_password=False, width=250, **kwargs):
        super().__init__(parent, bg=COLOR_ACCENT_LIGHT, padx=1, pady=1, **kwargs)
        
        self.inner_frame = tk.Frame(self, bg=COLOR_WHITE, padx=8, pady=6)
        self.inner_frame.pack(fill="both", expand=True)
        
        show_char = "*" if is_password else ""
        self.entry = tk.Entry(
            self.inner_frame,
            bg=COLOR_WHITE,
            fg="#333333",
            bd=0,
            highlightthickness=0,
            show=show_char,
            insertbackground=COLOR_PRIMARY_DARK,
            font=("Arial", 11)
        )
        self.entry.pack(fill="x", expand=True)
        
        # Focus events
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
    def get(self):
        return self.entry.get()
        
    def delete(self, first, last=None):
        self.entry.delete(first, last)
        
    def insert(self, index, string):
        self.entry.insert(index, string)
        
    def _on_focus_in(self, event):
        self.configure(bg=COLOR_ACTIVE_HOVER)
        
    def _on_focus_out(self, event):
        self.configure(bg=COLOR_ACCENT_LIGHT)

class ScrollableTable(tk.Frame):
    def __init__(self, parent, headers, col_widths, col_anchors=None, bg=COLOR_WHITE):
        super().__init__(parent, bg=bg)
        
        self.headers = headers
        self.col_widths = col_widths
        # Per-column text anchor: "w"=left, "center", "e"=right
        self.col_anchors = col_anchors or (["center"] * len(headers))
        
        # Calculate total width of all columns
        self.total_width = sum(w if w > 0 else 150 for w in col_widths)
        self._bg = bg
        
        # Vertical scrollbar for rows
        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        
        # Main canvas that holds everything (header + rows)
        self.main_canvas = tk.Canvas(self, bg=bg, highlightthickness=0,
                                     yscrollcommand=self.scrollbar.set)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.configure(command=self.main_canvas.yview)
        
        # Inner frame inside canvas
        self.inner_frame = tk.Frame(self.main_canvas, bg=bg)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # ── Header ──────────────────────────────────────────────────
        header_wrapper = tk.Frame(self.inner_frame, bg=COLOR_ACCENT_GOLD)
        header_wrapper.pack(fill="x", side="top")

        self.header_frame = tk.Frame(header_wrapper, bg=COLOR_PRIMARY_DARK, height=40)
        self.header_frame.pack(fill="x", side="top", padx=0, pady=(0, 2))  # 2px gold underline
        self.header_frame.pack_propagate(False)
        
        self._header_cells = []
        for i, (h, w) in enumerate(zip(headers, col_widths)):
            width_val = w if w > 0 else 150
            f = tk.Frame(self.header_frame, bg=COLOR_PRIMARY_DARK, width=width_val, height=40)
            f.pack(side="left", fill="y")
            f.pack_propagate(False)
            
            lbl = tk.Label(
                f,
                text=h,
                bg=COLOR_PRIMARY_DARK,
                fg=COLOR_ACCENT_GOLD,
                font=("Segoe UI", 9, "bold"),
                anchor="center",
                padx=6
            )
            lbl.pack(fill="both", expand=True)
            self._header_cells.append(f)
            
            # Vertical divider between columns
            if i < len(headers) - 1:
                sep = tk.Frame(self.header_frame, bg="#5A7A6A", width=1)
                sep.pack(side="left", fill="y", pady=6)
        
        # ── Row container ───────────────────────────────────────────
        self.row_frame = tk.Frame(self.inner_frame, bg=bg)
        self.row_frame.pack(fill="both", expand=True)
        
        # Outer border line around row area
        row_border = tk.Frame(self.inner_frame, bg="#D0DDD9", height=1)
        row_border.pack(fill="x", side="bottom")
        
        # Update scroll region when content changes
        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        self.main_canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Enable mouse wheel scrolling
        self.main_canvas.bind("<Enter>", self._bind_mousewheel)
        self.main_canvas.bind("<Leave>", self._unbind_mousewheel)
        self.rows = []

    def _on_inner_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        """When parent resizes, stretch columns proportionally to fill the width."""
        canvas_width = event.width
        extra = max(0, canvas_width - self.total_width)
        
        for i, (cell, w) in enumerate(zip(self._header_cells, self.col_widths)):
            base = w if w > 0 else 150
            proportion = base / self.total_width
            new_w = base + int(extra * proportion)
            cell.configure(width=new_w)
            
        # Also update all existing rows
        for row_wrapper in self.rows:
            children = row_wrapper.winfo_children()
            if not children:
                continue
            r_frame = children[0]
            
            col_idx = 0
            child_idx = 0
            grid_children = r_frame.winfo_children()
            
            for i, w in enumerate(self.col_widths[:-1]):
                base = w if w > 0 else 150
                proportion = base / self.total_width
                new_w = base + int(extra * proportion)
                
                r_frame.grid_columnconfigure(col_idx, minsize=new_w, weight=base)
                
                # Check grid_children:
                # The labels are in order, skip separators
                if child_idx < len(grid_children):
                    lbl = grid_children[child_idx]
                    if isinstance(lbl, tk.Label):
                        lbl.configure(wraplength=max(10, new_w - 24))
                    child_idx += 1
                col_idx += 1
                
                if i < len(self.col_widths) - 2:
                    col_idx += 1
                    if child_idx < len(grid_children):
                        child_idx += 1 # skip separator
                        
            # Last column (Action column)
            act_w = self.col_widths[-1]
            proportion = act_w / self.total_width
            new_w = act_w + int(extra * proportion)
            r_frame.grid_columnconfigure(col_idx, minsize=new_w, weight=act_w)

        # Always stretch inner_frame to fill canvas width
        self.main_canvas.itemconfig(self.canvas_window, width=max(canvas_width, self.total_width))

    def _bind_mousewheel(self, event):
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.main_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.scrollbar.winfo_exists():
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def clear(self):
        for widget in self.row_frame.winfo_children():
            widget.destroy()
        self.rows = []

        
    def add_row(self, values, action_creator=None):
        row_idx = len(self.rows)
        # Alternating row colors
        bg_color = "#FFFFFF" if row_idx % 2 == 0 else "#F0F5F3"
        border_color = "#DDE8E4"

        # Row wrapper: 1px bottom border via colored outer frame
        row_wrapper = tk.Frame(self.row_frame, bg=border_color)
        row_wrapper.pack(fill="x")

        r_frame = tk.Frame(row_wrapper, bg=bg_color)
        r_frame.pack(fill="x", padx=0, pady=(0, 1))
        
        cell_frames = []
        cell_labels = []
        
        # Data columns with vertical separators
        col_index = 0
        for i, (val, w) in enumerate(zip(values, self.col_widths[:-1])):
            width_val = w if w > 0 else 150
            anchor = self.col_anchors[i] if i < len(self.col_anchors) else "center"
            
            # Configure column width in the grid layout of r_frame
            r_frame.grid_columnconfigure(col_index, minsize=width_val, weight=width_val)
            
            lbl = tk.Label(
                r_frame,
                text=str(val),
                bg=bg_color,
                fg="#2C3E35",
                font=("Segoe UI", 9),
                anchor=anchor,
                padx=12,
                pady=8,
                justify="center",
                wraplength=width_val - 24
            )
            lbl.grid(row=0, column=col_index, sticky="nsew")
            cell_labels.append(lbl)
            col_index += 1

            # Thin vertical separator
            if i < len(self.col_widths) - 2:
                r_frame.grid_columnconfigure(col_index, minsize=1, weight=0)
                sep = tk.Frame(r_frame, bg="#DDE8E4", width=1)
                sep.grid(row=0, column=col_index, sticky="ns", pady=5)
                cell_frames.append(sep)
                col_index += 1

        # Action column (last column)
        act_w = self.col_widths[-1]
        width_val = act_w if act_w > 0 else 150
        r_frame.grid_columnconfigure(col_index, minsize=width_val, weight=width_val)
        
        act_frame = tk.Frame(r_frame, bg=bg_color)
        act_frame.grid(row=0, column=col_index, sticky="nsew")
        cell_frames.append(act_frame)
        
        if action_creator:
            act_wrapper = tk.Frame(act_frame, bg=bg_color)
            act_wrapper.pack(expand=True, anchor="center")
            cell_frames.append(act_wrapper)
            action_creator(act_wrapper, bg_color)
        
        # ── Hover highlight ──────────────────────────────────────────
        HOVER_BG = "#E3F0EC"
        HOVER_FG = "#1A3028"

        def on_enter(e, _bg=bg_color):
            r_frame.configure(bg=HOVER_BG)
            for cf in cell_frames:
                try:
                    if cf.winfo_exists():
                        cf.configure(bg=HOVER_BG)
                except Exception:
                    pass
            for cl in cell_labels:
                try:
                    if cl.winfo_exists():
                        cl.configure(bg=HOVER_BG, fg=HOVER_FG)
                except Exception:
                    pass

        def on_leave(e, _bg=bg_color):
            r_frame.configure(bg=_bg)
            for cf in cell_frames:
                try:
                    if cf.winfo_exists():
                        cf.configure(bg=_bg)
                except Exception:
                    pass
            for cl in cell_labels:
                try:
                    if cl.winfo_exists():
                        cl.configure(bg=_bg, fg="#2C3E35")
                except Exception:
                    pass

        for widget in [r_frame] + cell_frames + cell_labels:
            try:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
            except Exception:
                pass
            
        self.rows.append(row_wrapper)



def configure_treeview_style(style=None):
    """Apply a polished, consistent style to all ttk.Treeview widgets."""
    if style is None:
        style = ttk.Style()

    style.theme_use("clam")

    # ── Treeview overall ────────────────────────────────────────────
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground="#2C3E35",
        fieldbackground="#FFFFFF",
        font=("Segoe UI", 9),
        rowheight=34,
        bordercolor="#D0DDD9",
        borderwidth=1,
        relief="flat",
    )
    style.layout("Treeview", [
        ("Treeview.treearea", {"sticky": "nswe"})
    ])

    # ── Header ──────────────────────────────────────────────────────
    style.configure(
        "Treeview.Heading",
        background=COLOR_PRIMARY_DARK,
        foreground=COLOR_ACCENT_GOLD,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        padding=(10, 6),
        borderwidth=0,
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#3A4D40")],
        foreground=[("active", COLOR_ACCENT_GOLD)],
    )

    # ── Selected row ─────────────────────────────────────────────────
    style.map(
        "Treeview",
        background=[("selected", COLOR_ACTIVE_HOVER)],
        foreground=[("selected", "#FFFFFF")],
    )
