import tkinter as tk
from tkinter import messagebox
import db
from ui import ui_helpers

class LoginViewMixin:
    def show_login_view(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        self.geometry("800x500")
        self.resizable(False, False)
        self.center_window(800, 500)
        
        # Container
        self.login_frame = tk.Frame(self, bg=ui_helpers.COLOR_BG_LIGHT)
        self.login_frame.pack(fill="both", expand=True)
        
        # 1. Left Panel (Visual/Branding - 50%)
        self.left_panel = tk.Canvas(self.login_frame, width=400, height=500, highlightthickness=0)
        self.left_panel.pack(side="left", fill="both")
        
        # Redraw gradient on configure
        self.left_panel.bind("<Configure>", lambda e: ui_helpers.draw_gradient_canvas(
            self.left_panel, e.width, e.height, ui_helpers.COLOR_PRIMARY_DARK, ui_helpers.COLOR_ACTIVE_HOVER
        ))
        
        # Load logo icon
        self.logo_photo = ui_helpers.generate_logo_icon(size=(120, 120))
        self.left_panel.create_image(200, 110, image=self.logo_photo)
        
        # Divider line
        self.left_panel.create_line(60, 190, 340, 190, fill=ui_helpers.COLOR_ACCENT_LIGHT, width=1)
        
        # Title
        self.left_panel.create_text(
            200, 230, 
            text="HỆ THỐNG QUẢN LÝ", 
            fill=ui_helpers.COLOR_WHITE, 
            font=("Arial", 18, "bold"), 
            justify="center"
        )
        self.left_panel.create_text(
            200, 270, 
            text="TRUNG TÂM DỊCH VỤ & SỬA CHỮA XE", 
            fill=ui_helpers.COLOR_WHITE, 
            font=("Arial", 14, "bold"), 
            justify="center"
        )
        
        # Divider line 2
        self.left_panel.create_line(60, 320, 340, 320, fill=ui_helpers.COLOR_ACCENT_LIGHT, width=1)
        
        # Subtitle
        self.left_panel.create_text(
            200, 360, 
            text="Hiệu Quả - Tin Cậy - Sửa Chữa Thông Minh", 
            fill="#B4C9C2",  # Light tint
            font=("Arial", 11, "italic"), 
            justify="center"
        )
        
        # 2. Right Panel (Login form - 50%)
        self.right_panel = tk.Frame(self.login_frame, bg=ui_helpers.COLOR_BG_LIGHT, width=400, height=500)
        self.right_panel.pack(side="right", fill="both", expand=True)
        self.right_panel.pack_propagate(False)
        
        # Form Card (Center of right panel)
        self.shadow_frame = tk.Frame(self.right_panel, bg="#E2E6E4", padx=1, pady=1)
        self.shadow_frame.place(relx=0.5, rely=0.5, width=340, height=380, anchor="center")
        
        self.card_frame = tk.Frame(self.shadow_frame, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        self.card_frame.pack(fill="both", expand=True)
        
        # Title "Welcome Back"
        self.welcome_lbl = tk.Label(
            self.card_frame, 
            text="Welcome Back", 
            bg=ui_helpers.COLOR_WHITE, 
            fg=ui_helpers.COLOR_PRIMARY_DARK, 
            font=("Arial", 18, "bold")
        )
        self.welcome_lbl.pack(anchor="w", pady=(10, 25))
        
        # Username Input
        self.user_lbl = tk.Label(
            self.card_frame, 
            text="Tên đăng nhập / Username", 
            bg=ui_helpers.COLOR_WHITE, 
            fg="#666666", 
            font=("Arial", 9, "bold")
        )
        self.user_lbl.pack(anchor="w", pady=(0, 5))
        
        self.username_input = ui_helpers.CustomEntry(self.card_frame)
        self.username_input.pack(fill="x", pady=(0, 15))
        
        # Password Input
        self.pass_lbl = tk.Label(
            self.card_frame, 
            text="Mật khẩu / Password", 
            bg=ui_helpers.COLOR_WHITE, 
            fg="#666666", 
            font=("Arial", 9, "bold")
        )
        self.pass_lbl.pack(anchor="w", pady=(0, 5))
        
        self.password_input = ui_helpers.CustomEntry(self.card_frame, is_password=True)
        self.password_input.pack(fill="x", pady=(0, 25))
        
        # Login Button
        self.login_btn = tk.Button(
            self.card_frame, 
            text="Đăng nhập", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE, 
            bd=0, 
            relief="flat", 
            font=("Arial", 11, "bold"), 
            cursor="hand2",
            command=self.perform_login
        )
        self.login_btn.pack(fill="x", ipady=8)
        
        # Button hover bindings
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
    def perform_login(self):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        
        if not username or not password:
            messagebox.showerror("Lỗi đăng nhập", "Vui lòng điền đầy đủ tên đăng nhập và mật khẩu!")
            return
            
        user = db.authenticate(username, password)
        if user:
            self.current_user = user
            self.show_main_shell()
        else:
            messagebox.showerror("Thất bại", "Tên đăng nhập hoặc mật khẩu không chính xác!")
