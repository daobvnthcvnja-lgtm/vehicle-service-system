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
    processed_path = os.path.join(base_dir, "logo_processed.png")
    raw_path = os.path.join(base_dir, "logo.png")
    
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
    def __init__(self, parent, headers, col_widths, bg=COLOR_WHITE):
        super().__init__(parent, bg=bg)
        
        self.headers = headers
        self.col_widths = col_widths
        
        # Calculate total width of all columns
        self.total_width = sum(w if w > 0 else 150 for w in col_widths)
        
        # Horizontal Canvas and Scrollbar
        self.h_canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.h_canvas.xview)
        self.h_canvas.configure(xscrollcommand=self.hsb.set)
        
        self.h_canvas.pack(side="top", fill="both", expand=True)
        self.hsb.pack(side="bottom", fill="x")
        
        # Table container inside the horizontal canvas
        self.table_container = tk.Frame(self.h_canvas, bg=bg)
        self.h_canvas.create_window((0, 0), window=self.table_container, anchor="nw")
        
        self.table_container.bind(
            "<Configure>",
            lambda e: self.h_canvas.configure(scrollregion=self.h_canvas.bbox("all"))
        )
        
        # Header Container inside table container
        self.header_frame = tk.Frame(self.table_container, bg=COLOR_HEADER_BG, width=self.total_width, height=35)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        # Draw headers matching custom widths
        for h, w in zip(headers, col_widths):
            width_val = w if w > 0 else 150
            f = tk.Frame(self.header_frame, bg=COLOR_HEADER_BG, width=width_val, height=35)
            f.pack(side="left", fill="y")
            f.pack_propagate(False)
            
            lbl = tk.Label(
                f, 
                text=h, 
                bg=COLOR_HEADER_BG, 
                fg=COLOR_WHITE, 
                font=("Arial", 10, "bold"), 
                anchor="w", 
                padx=10
            )
            lbl.pack(fill="both", expand=True)
            
        # Row area inside table container
        row_area = tk.Frame(self.table_container, bg=bg)
        row_area.pack(fill="both", expand=True)
        
        # Canvas and Scrollbar for rows
        self.canvas = tk.Canvas(row_area, bg=bg, highlightthickness=0, width=self.total_width)
        self.scrollbar = ttk.Scrollbar(row_area, orient="vertical", command=self.canvas.yview)
        self.row_frame = tk.Frame(self.canvas, bg=bg, width=self.total_width)
        
        self.row_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.row_frame, anchor="nw")
        # Ensure row canvas window width stays fixed to total_width
        self.canvas.itemconfig(self.canvas_window, width=self.total_width)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.rows = []

    def _on_mousewheel(self, event):
        # Ensure scrollbar exists before scrolling
        if self.scrollbar.winfo_exists():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def clear(self):
        for widget in self.row_frame.winfo_children():
            widget.destroy()
        self.rows = []
        
    def add_row(self, values, action_creator=None):
        row_idx = len(self.rows)
        bg_color = COLOR_WHITE if row_idx % 2 == 0 else COLOR_BG_LIGHT
        
        r_frame = tk.Frame(self.row_frame, bg=bg_color, height=38, width=self.total_width)
        r_frame.pack(fill="x", pady=1)
        r_frame.pack_propagate(False)
        
        # Display all values except the last column (which represents the action buttons)
        for val, w in zip(values, self.col_widths[:-1]):
            width_val = w if w > 0 else 150
            f = tk.Frame(r_frame, bg=bg_color, width=width_val, height=38)
            f.pack(side="left", fill="y")
            f.pack_propagate(False)
            
            lbl = tk.Label(
                f, 
                text=str(val), 
                bg=bg_color, 
                fg="#333333", 
                font=("Arial", 9), 
                anchor="w", 
                padx=10
            )
            lbl.pack(fill="both", expand=True)
            
        # Action column
        act_w = self.col_widths[-1]
        width_val = act_w if act_w > 0 else 150
        act_frame = tk.Frame(r_frame, bg=bg_color, width=width_val, height=38)
        act_frame.pack(side="left", fill="y")
        act_frame.pack_propagate(False)
        
        if action_creator:
            action_creator(act_frame, bg_color)
            
        self.rows.append(r_frame)
