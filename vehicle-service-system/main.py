import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
from datetime import datetime
from PIL import Image, ImageTk

# Import local modules
import db
import ui_helpers
from tkcalendar import DateEntry
from fpdf import FPDF
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GarageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Trung Tâm Dịch Vụ Và Sửa Chữa Xe")
        self.geometry("800x500")
        self.resizable(False, False)
        
        # Center window
        self.center_window(800, 500)
        
        # Initialize DB tables if not present
        db.init_db()
        
        # Global state
        self.current_user = None  # Stores dict: {id, name, username, role}
        
        # Render Login View initially
        self.show_login_view()
        
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

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
        
        # We need to overlay text and icons on the canvas
        # Since Tkinter canvas overlays are drawn items:
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
        # To simulate a shadow, we can make a outer frame representing shadow and inner white card
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

    def show_main_shell(self):
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()
            
        # Set large window size
        self.geometry("1280x800")
        self.resizable(True, True)
        self.center_window(1280, 800)
        
        # Root layout grid: Left sidebar, Right main content
        self.main_container = tk.Frame(self, bg=ui_helpers.COLOR_BG_LIGHT)
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar: 1/4 width (width = 320 for 1280 screen)
        self.sidebar_frame = tk.Frame(self.main_container, bg=ui_helpers.COLOR_PRIMARY_DARK, width=320)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        # Logo inside sidebar top
        self.sb_logo_canvas = tk.Canvas(
            self.sidebar_frame, 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            height=120, 
            highlightthickness=0
        )
        self.sb_logo_canvas.pack(fill="x", pady=10)
        
        self.sidebar_logo_photo = ui_helpers.generate_logo_icon(size=(80, 80))
        self.sb_logo_canvas.create_image(160, 60, image=self.sidebar_logo_photo)
        
        # Faint line below logo in sidebar
        sb_line = tk.Frame(self.sidebar_frame, bg=ui_helpers.COLOR_ACTIVE_HOVER, height=1)
        sb_line.pack(fill="x", padx=20, pady=(0, 20))
        
        # Content frame on the right: fits 3/4 width, has header on top
        self.content_container = tk.Frame(self.main_container, bg=ui_helpers.COLOR_BG_LIGHT)
        self.content_container.pack(side="right", fill="both", expand=True)
        
        # Header bar (1/10 height: 80px)
        self.header_frame = tk.Frame(self.content_container, bg=ui_helpers.COLOR_HEADER_BG, height=80)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        # Header text
        self.header_title = tk.Label(
            self.header_frame, 
            text="TRANG CHỦ / DASHBOARD", 
            bg=ui_helpers.COLOR_HEADER_BG, 
            fg=ui_helpers.COLOR_WHITE, 
            font=("Arial", 16, "bold"),
            padx=20
        )
        self.header_title.pack(side="left", fill="y")
        
        # Header user info
        user_info_str = f"{self.current_user['name']} ({'Quản lý' if self.current_user['role'] == 'QuanLy' else 'Nhân viên'})"
        self.header_user = tk.Label(
            self.header_frame, 
            text=user_info_str, 
            bg=ui_helpers.COLOR_HEADER_BG, 
            fg=ui_helpers.COLOR_WHITE, 
            font=("Arial", 11, "bold"),
            padx=20
        )
        self.header_user.pack(side="right", fill="y")
        
        # View area for loaded screens
        self.view_frame = tk.Frame(self.content_container, bg=ui_helpers.COLOR_BG_LIGHT)
        self.view_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Build Navigation Menu based on user role
        self.nav_buttons = []
        self.active_nav_btn = None
        
        role = self.current_user["role"]
        if role == "QuanLy":
            menu_items = [
                ("Thống kê", self.load_manager_dashboard),
                ("Dịch vụ sửa chữa", self.load_manager_services),
                ("Quản lý nhân viên", self.load_manager_staff),
                ("Hóa đơn", self.load_manager_invoices),
                ("Chăm sóc khách hàng", self.load_manager_customer_care)
            ]
        else:  # NhanVien
            menu_items = [
                ("Thông tin khách hàng", self.load_staff_customers),
                ("Phiếu sửa chữa", self.load_staff_slips),
                ("Thanh toán", self.load_staff_payments)
            ]
            
        # Draw navigation buttons
        for title, callback in menu_items:
            btn = tk.Button(
                self.sidebar_frame, 
                text=title, 
                bg=ui_helpers.COLOR_ACCENT_LIGHT, 
                fg="#2C3E35",  # Charcoal green text
                activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
                activeforeground=ui_helpers.COLOR_WHITE,
                bd=0, 
                relief="flat", 
                font=("Arial", 12, "bold"), 
                padx=20, 
                pady=12,
                cursor="hand2"
            )
            btn.pack(fill="x", padx=20, pady=5)
            
            # Setup hover/click triggers
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_hover(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_leave(b))
            btn.configure(command=lambda c=callback, b=btn: self.on_nav_click(c, b))
            
            self.nav_buttons.append(btn)
            
        # Logout button at bottom of sidebar
        self.logout_icon_photo = ui_helpers.generate_logout_icon()
        self.logout_btn = tk.Button(
            self.sidebar_frame, 
            text=" Đăng xuất", 
            image=self.logout_icon_photo,
            compound="left",
            bg=ui_helpers.COLOR_ACCENT_LIGHT, 
            fg=ui_helpers.COLOR_RED,  # Red text color
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 12, "bold"), 
            pady=12,
            cursor="hand2",
            command=self.perform_logout
        )
        self.logout_btn.pack(side="bottom", fill="x", padx=20, pady=30)
        self.logout_btn.bind("<Enter>", lambda e: self.logout_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        self.logout_btn.bind("<Leave>", lambda e: self.logout_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT))
        
        # Load first view
        if self.nav_buttons:
            self.on_nav_click(menu_items[0][1], self.nav_buttons[0])

    def on_nav_hover(self, btn):
        if btn != self.active_nav_btn:
            btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE)

    def on_nav_leave(self, btn):
        if btn != self.active_nav_btn:
            btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35")

    def on_nav_click(self, callback, btn):
        # Reset previous active button
        if self.active_nav_btn:
            self.active_nav_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35")
            
        self.active_nav_btn = btn
        btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE)
        
        # Change header title
        self.header_title.configure(text=btn.cget("text").upper())
        
        # Call page drawer
        callback()

    def perform_logout(self):
        confirm = messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?")
        if confirm:
            db.log_action(self.current_user["id"], "Đăng xuất khỏi hệ thống")
            self.current_user = None
            self.show_login_view()

    def clear_view_frame(self):
        for widget in self.view_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # REPAIR STAFF VIEWS
    # ==========================================

    def load_staff_customers(self):
        self.clear_view_frame()
        
        # View Title or Description (top 1/10 area is header)
        # Search bar and Add button at top
        top_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        top_bar.pack(fill="x", pady=(0, 10))
        
        search_lbl = tk.Label(top_bar, text="Tìm kiếm khách hàng: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold"))
        search_lbl.pack(side="left", padx=(0, 5))
        
        search_entry = ui_helpers.CustomEntry(top_bar, width=300)
        search_entry.pack(side="left", fill="y", padx=5)
        
        add_btn = tk.Button(
            top_bar, 
            text=" + Thêm khách hàng", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 10, "bold"), 
            padx=15, 
            pady=8,
            cursor="hand2",
            command=self.open_add_customer_dialog
        )
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        # Divider Line centered with margins
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # Table frame
        table_frame = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_WHITE)
        table_frame.pack(fill="both", expand=True)
        
        # Columns
        columns = ("MaKH", "HoTen", "SoDienThoai", "DiaChi")
        self.customer_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.customer_tree.heading("MaKH", text="Mã KH")
        self.customer_tree.heading("HoTen", text="Họ và Tên")
        self.customer_tree.heading("SoDienThoai", text="Số điện thoại")
        self.customer_tree.heading("DiaChi", text="Địa chỉ")
        
        self.customer_tree.column("MaKH", width=100, anchor="center")
        self.customer_tree.column("HoTen", width=250, anchor="w")
        self.customer_tree.column("SoDienThoai", width=180, anchor="center")
        self.customer_tree.column("DiaChi", width=350, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Fetch initial customer list
        self.refresh_customer_table()
        
        # Search on Enter
        search_entry.entry.bind("<Return>", lambda e: self.refresh_customer_table(search_entry.get()))

    def refresh_customer_table(self, query=""):
        # Clear items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
            
        rows = db.get_customers(query)
        for r in rows:
            self.customer_tree.insert("", "end", values=r)

    def open_add_customer_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm Khách Hàng Mới")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.grab_set() # Modal dialog
        
        # Center dialog on screen
        self.center_toplevel(dialog, 400, 350)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        title_lbl = tk.Label(form_frame, text="THÔNG TIN KHÁCH HÀNG", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 12, "bold"))
        title_lbl.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # ID (Auto-increment, read-only)
        tk.Label(form_frame, text="Mã KH:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        id_val = tk.Label(form_frame, text="Tự động tăng (Auto)", bg=ui_helpers.COLOR_WHITE, fg="#999999", font=("Arial", 10, "italic"))
        id_val.grid(row=1, column=1, sticky="w", pady=10)
        
        # Name
        tk.Label(form_frame, text="Tên khách hàng *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
        name_entry = ui_helpers.CustomEntry(form_frame)
        name_entry.grid(row=2, column=1, sticky="ew", pady=10)
        
        # Phone
        tk.Label(form_frame, text="Số điện thoại:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=10)
        phone_entry = ui_helpers.CustomEntry(form_frame)
        phone_entry.grid(row=3, column=1, sticky="ew", pady=10)
        
        # Address
        tk.Label(form_frame, text="Địa chỉ:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=10)
        addr_entry = ui_helpers.CustomEntry(form_frame)
        addr_entry.grid(row=4, column=1, sticky="ew", pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="e")
        
        cancel_btn = tk.Button(
            btn_frame, 
            text="Hủy bỏ", 
            bg=ui_helpers.COLOR_BG_LIGHT, 
            fg="#666666", 
            bd=0, 
            relief="flat", 
            font=("Arial", 9, "bold"), 
            padx=15, 
            pady=6,
            cursor="hand2",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(
            btn_frame, 
            text="Lưu dữ liệu", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 9, "bold"), 
            padx=15, 
            pady=6,
            cursor="hand2",
            command=lambda: self.save_new_customer(name_entry.get(), phone_entry.get(), addr_entry.get(), dialog)
        )
        save_btn.pack(side="right", padx=5)
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def save_new_customer(self, name, phone, address, dialog):
        if not name.strip():
            messagebox.showerror("Lỗi dữ liệu", "Vui lòng nhập tên khách hàng!", parent=dialog)
            return
            
        try:
            db.add_customer(name.strip(), phone.strip(), address.strip(), self.current_user["id"])
            messagebox.showinfo("Thành công", "Đã thêm khách hàng mới thành công!", parent=dialog)
            dialog.destroy()
            self.refresh_customer_table()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể lưu khách hàng:\n{e}", parent=dialog)

    def center_toplevel(self, toplevel, width, height):
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        toplevel.geometry(f"{width}x{height}+{x}+{y}")

    def load_staff_slips(self):
        self.clear_view_frame()
        
        # Top tools
        top_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        top_bar.pack(fill="x", pady=(0, 10))
        
        search_lbl = tk.Label(top_bar, text="Tìm kiếm phiếu sửa chữa: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold"))
        search_lbl.pack(side="left", padx=(0, 5))
        
        search_entry = ui_helpers.CustomEntry(top_bar, width=300)
        search_entry.pack(side="left", fill="y", padx=5)
        
        add_btn = tk.Button(
            top_bar, 
            text=" + Tạo phiếu sửa chữa", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 10, "bold"), 
            padx=15, 
            pady=8,
            cursor="hand2",
            command=self.open_create_slip_dialog
        )
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        # Divider Line
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # ScrollableTable of Slips
        self.slip_table = ui_helpers.ScrollableTable(
            self.view_frame,
            headers=["Mã Phiếu", "Tên Phiếu", "Khách Hàng", "Tính Chất", "Lịch Hẹn", "Ngày Tạo", "Thao tác"],
            col_widths=[80, 180, 220, 100, 200, 150, 150]
        )
        self.slip_table.pack(fill="both", expand=True)
        
        self.refresh_slips_table(search_entry)
        
        # Search on Enter key press
        search_entry.entry.bind("<Return>", lambda e: self.refresh_slips_table(search_entry))

    def refresh_slips_table(self, search_entry):
        self.slip_table.clear()
        query = search_entry.get().strip()
        rows = db.get_slips(query)
        for r in rows:
            nature_text = "Lấy liền" if r["nature"] == "LayLien" else "Hẹn"
            if r["nature"] == "Hen":
                sched_text = f"Từ {r['start_date']} - {r['end_date']}"
            else:
                sched_text = "N/A"
                
            cust_text = f"[{r['customer_id']}] {r['customer_name']}"
            
            def create_actions(frame, bg_c, slip_data=r):
                # Edit (Sửa) button
                edit_btn = tk.Button(
                    frame, text="Sửa", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
                    bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                    command=lambda: self.open_create_slip_dialog(slip_data)
                )
                edit_btn.pack(side="left", padx=5, pady=5)
                edit_btn.bind("<Enter>", lambda e: edit_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                edit_btn.bind("<Leave>", lambda e: edit_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35"))
                
                # Delete (Xóa) button
                del_btn = tk.Button(
                    frame, text="Xóa", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED,
                    bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                    command=lambda: self.confirm_delete_slip(slip_data["id"])
                )
                del_btn.pack(side="left", padx=5, pady=5)
                del_btn.bind("<Enter>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                del_btn.bind("<Leave>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED))

            self.slip_table.add_row(
                values=[r["id"], r["title"], cust_text, nature_text, sched_text, r["created_at"]],
                action_creator=create_actions
            )

    def open_create_slip_dialog(self, slip_data=None):
        # Slip creation/editing dialog
        dialog = tk.Toplevel(self)
        dialog.title("Cập Nhật Phiếu Sửa Chữa" if slip_data else "Tạo Phiếu Sửa Chữa Mới")
        dialog.geometry("600x650")
        dialog.resizable(False, False)
        # Note: dialog.grab_set() is removed to allow DateEntry calendar navigation month/year!
        
        self.center_toplevel(dialog, 600, 650)
        
        # Scrollable form if content overflows
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(
            form_frame, 
            text="CẬP NHẬT PHIẾU SỰA CHỮA XE" if slip_data else "TẠO PHIẾU SỬA CHỮA XE", 
            bg=ui_helpers.COLOR_WHITE, 
            fg=ui_helpers.COLOR_PRIMARY_DARK, 
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Slip Name
        tk.Label(form_frame, text="Tên phiếu *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        slip_name_entry = ui_helpers.CustomEntry(form_frame)
        slip_name_entry.pack(fill="x", pady=(0, 10))
        if slip_data:
            slip_name_entry.entry.insert(0, slip_data["title"])
        
        # Customer Droplist: ID-Name-Address
        tk.Label(form_frame, text="Thông tin khách hàng *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        customers = db.get_customers()
        cust_options = [f"{c[0]} - {c[1]} - {c[3]}" for c in customers]
        
        cust_combo = ttk.Combobox(form_frame, values=cust_options, state="readonly", font=("Arial", 10))
        cust_combo.pack(fill="x", pady=(0, 10))
        if cust_options:
            cust_combo.current(0)
            
        if slip_data:
            cust_match = next((opt for opt in cust_options if opt.startswith(f"{slip_data['customer_id']} - ")), None)
            if cust_match:
                cust_combo.current(cust_options.index(cust_match))
            
        # Services Droplist containing Cascade Menu
        tk.Label(form_frame, text="Dịch vụ sửa chữa * (Chọn dịch vụ từ Menu):", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        selected_services = []  # List of dicts/tuples: (MaDV, TenDichVu, Gia, TenLoai)
        
        # Container to show selected services
        services_container = tk.LabelFrame(form_frame, text=" Các dịch vụ đã chọn ", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold"))
        services_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollable service area inside container
        sv_canvas = tk.Canvas(services_container, bg=ui_helpers.COLOR_WHITE, highlightthickness=0, height=80)
        sv_scroll = ttk.Scrollbar(services_container, orient="vertical", command=sv_canvas.yview)
        sv_frame = tk.Frame(sv_canvas, bg=ui_helpers.COLOR_WHITE)
        
        sv_frame.bind(
            "<Configure>",
            lambda e: sv_canvas.configure(scrollregion=sv_canvas.bbox("all"))
        )
        sv_canvas.create_window((0,0), window=sv_frame, anchor="nw")
        sv_canvas.configure(yscrollcommand=sv_scroll.set)
        
        sv_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sv_scroll.pack(side="right", fill="y", pady=5)
        
        total_price_lbl = tk.Label(form_frame, text="Tổng cộng tạm tính: 0 đ", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 10, "bold"))
        total_price_lbl.pack(anchor="e", pady=(0, 5))
        
        def render_selected_services():
            # Clear frame
            for widget in sv_frame.winfo_children():
                widget.destroy()
            
            total = 0
            for idx, sv in enumerate(selected_services):
                row = tk.Frame(sv_frame, bg=ui_helpers.COLOR_WHITE, height=25)
                row.pack(fill="x", pady=2)
                
                lbl_text = f"[{sv[3]}] {sv[1]} - {sv[2]:,}đ"
                lbl = tk.Label(row, text=lbl_text, bg=ui_helpers.COLOR_WHITE, fg="#333333", font=("Arial", 9), anchor="w")
                lbl.pack(side="left", fill="both", expand=True)
                
                del_btn = tk.Button(
                    row, text="✕", bg=ui_helpers.COLOR_WHITE, fg="red", bd=0, font=("Arial", 8, "bold"),
                    command=lambda idx=idx: remove_service(idx), cursor="hand2"
                )
                del_btn.pack(side="right", padx=5)
                
                total += sv[2]
                
            total_price_lbl.configure(text=f"Tổng cộng tạm tính: {total:,} đ")
            
        def remove_service(index):
            selected_services.pop(index)
            render_selected_services()
            
        def add_service_to_list(sv_data):
            # sv_data is (MaDV, MaLoai, TenLoai, TenDichVu, Gia)
            # check duplicate
            if any(s[0] == sv_data[0] for s in selected_services):
                messagebox.showwarning("Lỗi", "Dịch vụ này đã có trong phiếu sửa chữa!", parent=dialog)
                return
            selected_services.append((sv_data[0], sv_data[3], sv_data[4], sv_data[2])) # MaDV, TenDichVu, Gia, TenLoai
            render_selected_services()

        # Cascade Menu builder button
        menu_btn = tk.Button(
            form_frame, text="✚ Chọn phân loại & dịch vụ sửa chữa...", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=10, pady=5, cursor="hand2"
        )
        menu_btn.pack(fill="x", pady=(0, 10))
        
        # Build Cascade Menu
        service_menu = tk.Menu(dialog, tearoff=0)
        
        # Fetch categories
        cats = db.get_categories()
        for c in cats:
            sub_menu = tk.Menu(service_menu, tearoff=0)
            # Fetch services in this category
            services = db.get_services(category_id=c[0])
            if not services:
                sub_menu.add_command(label="(Trống)", state="disabled")
            for sv in services:
                # sv is (MaDV, MaLoai, TenLoai, TenDichVu, Gia)
                label_text = f"{sv[3]} - {sv[4]:,}đ"
                sub_menu.add_command(
                    label=label_text, 
                    command=lambda item=sv: add_service_to_list(item)
                )
            service_menu.add_cascade(label=c[1], menu=sub_menu)
            
        # Bind popup menu to button click
        def post_menu():
            # Get button absolute position
            x = menu_btn.winfo_rootx()
            y = menu_btn.winfo_rooty() + menu_btn.winfo_height()
            service_menu.post(x, y)
            
        menu_btn.configure(command=post_menu)
        
        # Nature: RadioButtonGroup ("Lấy liền" / "Hẹn")
        tk.Label(form_frame, text="Tính chất sửa chữa *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        nature_var = tk.StringVar(value="LayLien")
        nat_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        nat_frame.pack(fill="x", pady=(0, 10))
        
        # Date Picker Frame (collapsible)
        date_picker_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        
        # Date Pickers
        tk.Label(date_picker_frame, text="Từ ngày:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        start_date_picker = DateEntry(date_picker_frame, width=15, background=ui_helpers.COLOR_PRIMARY_DARK, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        start_date_picker.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(date_picker_frame, text="Đến ngày:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w", padx=15)
        end_date_picker = DateEntry(date_picker_frame, width=15, background=ui_helpers.COLOR_PRIMARY_DARK, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        end_date_picker.grid(row=0, column=3, padx=5, pady=5)
        
        def on_nature_change():
            val = nature_var.get()
            if val == "Hen":
                date_picker_frame.pack(fill="x", pady=5, after=nat_frame)
            else:
                date_picker_frame.pack_forget()
                
        r1 = tk.Radiobutton(
            nat_frame, text="Lấy liền (Lấy ngay)", bg=ui_helpers.COLOR_WHITE, variable=nature_var, 
            value="LayLien", font=("Arial", 10), command=on_nature_change
        )
        r1.pack(side="left", padx=10)
        
        r2 = tk.Radiobutton(
            nat_frame, text="Hẹn lịch sửa chữa", bg=ui_helpers.COLOR_WHITE, variable=nature_var, 
            value="Hen", font=("Arial", 10), command=on_nature_change
        )
        r2.pack(side="left", padx=10)
        
        if slip_data:
            # Load active services from slip
            for s in slip_data["services"]:
                selected_services.append((s[0], s[1], s[2], s[3]))
            render_selected_services()
            
            # Load nature & dates
            nature_var.set(slip_data["nature"])
            on_nature_change()
            if slip_data["nature"] == "Hen":
                try:
                    start_date_picker.set_date(slip_data["start_date"])
                    end_date_picker.set_date(slip_data["end_date"])
                except Exception:
                    pass
        else:
            render_selected_services()
        
        # Bottom Actions
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(
            btn_frame, 
            text="Hủy bỏ", 
            bg=ui_helpers.COLOR_BG_LIGHT, 
            fg="#666666", 
            bd=0, 
            relief="flat", 
            font=("Arial", 9, "bold"), 
            padx=15, 
            pady=6,
            cursor="hand2",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        def save_slip():
            title = slip_name_entry.get().strip()
            cust_val = cust_combo.get()
            nature = nature_var.get()
            
            if not title:
                messagebox.showerror("Thiếu thông tin", "Vui lòng nhập tên phiếu!", parent=dialog)
                return
            if not cust_val:
                messagebox.showerror("Thiếu thông tin", "Vui lòng chọn khách hàng!", parent=dialog)
                return
            if not selected_services:
                messagebox.showerror("Thiếu dịch vụ", "Vui lòng chọn ít nhất một dịch vụ!", parent=dialog)
                return
                
            kh_id = int(cust_val.split(" - ")[0])
            
            start_d = None
            end_d = None
            if nature == "Hen":
                start_d = start_date_picker.get()
                end_d = end_date_picker.get()
                
                # Verify start date <= end date
                try:
                    sd = datetime.strptime(start_d, "%Y-%m-%d")
                    ed = datetime.strptime(end_d, "%Y-%m-%d")
                    if sd > ed:
                        messagebox.showerror("Lỗi ngày hẹn", "Ngày hẹn bắt đầu không thể sau ngày kết thúc!", parent=dialog)
                        return
                except Exception as ex:
                    messagebox.showerror("Lỗi ngày hẹn", "Ngày hẹn không hợp lệ!", parent=dialog)
                    return
            
            # Map selected services to (MaDV, DonGia)
            sv_tuples = [(s[0], s[2]) for s in selected_services]
            
            try:
                if slip_data:
                    db.update_slip(slip_data["id"], title, kh_id, self.current_user["id"], nature, start_d, end_d, sv_tuples)
                    messagebox.showinfo("Thành công", "Đã cập nhật phiếu sửa chữa thành công!", parent=dialog)
                else:
                    db.create_slip(title, kh_id, self.current_user["id"], nature, start_d, end_d, sv_tuples)
                    messagebox.showinfo("Thành công", "Đã tạo phiếu sửa chữa thành công!", parent=dialog)
                dialog.destroy()
                if self.current_user["role"] == "QuanLy":
                    self.load_manager_customer_care()
                else:
                    self.load_staff_slips()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu phiếu sửa chữa:\n{e}", parent=dialog)
        
        save_btn = tk.Button(
            btn_frame, 
            text="Lưu phiếu", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 9, "bold"), 
            padx=15, 
            pady=6,
            cursor="hand2",
            command=save_slip
        )
        save_btn.pack(side="right", padx=5)
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def load_staff_payments(self):
        self.clear_view_frame()
        
        top_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        top_bar.pack(fill="x", pady=(0, 10))
        
        search_lbl = tk.Label(top_bar, text="Tìm hóa đơn/khách hàng: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold"))
        search_lbl.pack(side="left", padx=(0, 5))
        
        search_entry = ui_helpers.CustomEntry(top_bar, width=300)
        search_entry.pack(side="left", fill="y", padx=5)
        
        add_btn = tk.Button(
            top_bar, 
            text=" + Tạo hóa đơn & Thu tiền", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 10, "bold"), 
            padx=15, 
            pady=8,
            cursor="hand2",
            command=self.open_create_invoice_dialog
        )
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # Table frame
        table_frame = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_WHITE)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("MaHD", "MaPhieu", "TenPhieu", "KhachHang", "TongTien", "TrangThai", "PhuongThuc", "NgayThanhToan")
        self.invoice_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.invoice_tree.heading("MaHD", text="Mã HĐ")
        self.invoice_tree.heading("MaPhieu", text="Mã Phiếu")
        self.invoice_tree.heading("TenPhieu", text="Tên Phiếu")
        self.invoice_tree.heading("KhachHang", text="Khách Hàng")
        self.invoice_tree.heading("TongTien", text="Tổng Tiền")
        self.invoice_tree.heading("TrangThai", text="Trạng Thái")
        self.invoice_tree.heading("PhuongThuc", text="Phương Thức")
        self.invoice_tree.heading("NgayThanhToan", text="Ngày Thanh Toán")
        
        self.invoice_tree.column("MaHD", width=70, anchor="center")
        self.invoice_tree.column("MaPhieu", width=80, anchor="center")
        self.invoice_tree.column("TenPhieu", width=150, anchor="w")
        self.invoice_tree.column("KhachHang", width=220, anchor="w")
        self.invoice_tree.column("TongTien", width=120, anchor="e")
        self.invoice_tree.column("TrangThai", width=120, anchor="center")
        self.invoice_tree.column("PhuongThuc", width=120, anchor="center")
        self.invoice_tree.column("NgayThanhToan", width=180, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.invoice_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_invoices_table()
        
        # Search on Enter
        search_entry.entry.bind("<Return>", lambda e: self.refresh_invoices_table(search_entry.get()))

    def refresh_invoices_table(self, query=""):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
            
        rows = db.get_invoices(query)
        for r in rows:
            st = "Đã thanh toán" if r["status"] == "DaThanhToan" else "Chưa thanh toán"
            pm = "Chuyển khoản" if r["payment_method"] == "ChuyenKhoan" else ("Tiền mặt" if r["payment_method"] == "TienMat" else "N/A")
            pd = r["payment_date"] if r["payment_date"] else "N/A"
            self.invoice_tree.insert(
                "", "end", 
                values=(r["id"], r["slip_id"], r["slip_name"], r["customer_name"], f"{r['total_amount']:,}đ", st, pm, pd)
            )

    def open_create_invoice_dialog(self):
        # Dialog for checking out/creating invoice
        dialog = tk.Toplevel(self)
        dialog.title("Tạo Hóa Đơn & Thu Tiền")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 500, 550)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="CHI TIẾT HÓA ĐƠN", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 15))
        
        # ID Hoa Don (default: auto, show as Label)
        tk.Label(form_frame, text="Mã hóa đơn:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
        id_lbl = tk.Label(form_frame, text="Mã tự tăng sau khi lưu", bg=ui_helpers.COLOR_WHITE, fg="#999999", font=("Arial", 10, "italic"))
        id_lbl.pack(anchor="w", pady=(0, 10))
        
        # Slip Dropdown
        tk.Label(form_frame, text="Chọn phiếu sửa chữa *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
        
        # Fetch all slips
        slips = db.get_slips()
        slip_options = [f"{s['id']} - {s['title']}" for s in slips]
        
        slip_combo = ttk.Combobox(form_frame, values=slip_options, state="readonly", font=("Arial", 10))
        slip_combo.pack(fill="x", pady=(0, 10))
        
        # Read-only details
        details_frame = tk.Frame(form_frame, bg="#F9FBFB", bd=1, relief="solid", padx=15, pady=15, highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        details_frame.pack(fill="x", pady=(5, 10))
        
        # Customer
        tk.Label(details_frame, text="Khách hàng:", bg="#F9FBFB", fg="#666666", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        cust_val_lbl = tk.Label(details_frame, text="Chưa chọn phiếu", bg="#F9FBFB", fg="#333333", font=("Arial", 9))
        cust_val_lbl.grid(row=0, column=1, sticky="w", pady=4, padx=10)
        
        # Services
        tk.Label(details_frame, text="Dịch vụ thực hiện:", bg="#F9FBFB", fg="#666666", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="nw", pady=4)
        sv_val_lbl = tk.Label(details_frame, text="Chưa chọn phiếu", bg="#F9FBFB", fg="#333333", font=("Arial", 9), justify="left", wraplength=250)
        sv_val_lbl.grid(row=1, column=1, sticky="nw", pady=4, padx=10)
        
        # Price
        tk.Label(details_frame, text="Tổng tiền dịch vụ:", bg="#F9FBFB", fg="#666666", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        price_val_lbl = tk.Label(details_frame, text="0 đ", bg="#F9FBFB", fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 10, "bold"))
        price_val_lbl.grid(row=2, column=1, sticky="w", pady=4, padx=10)
        
        # Status
        tk.Label(details_frame, text="Trạng thái:", bg="#F9FBFB", fg="#666666", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        status_val_lbl = tk.Label(details_frame, text="Chưa thanh toán", bg="#F9FBFB", fg="orange", font=("Arial", 9, "bold"))
        status_val_lbl.grid(row=3, column=1, sticky="w", pady=4, padx=10)
        
        details_frame.columnconfigure(1, weight=1)
        
        # Payment Method: Dropdown (ChuyenKhoan / TienMat)
        tk.Label(form_frame, text="Phương thức thanh toán *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
        method_combo = ttk.Combobox(form_frame, values=["Chuyển khoản", "Tiền mặt"], state="readonly", font=("Arial", 10))
        method_combo.pack(fill="x", pady=(0, 15))
        method_combo.current(0)
        
        # Map selected slip data to populate labels
        active_invoice_id = [None] # Store local state in list for closure binding
        
        def on_slip_selected(event):
            selected_str = slip_combo.get()
            if not selected_str:
                return
            s_id = int(selected_str.split(" - ")[0])
            
            # Find slip in local lists
            slip_data = next((s for s in slips if s["id"] == s_id), None)
            if not slip_data:
                return
                
            cust_val_lbl.configure(text=f"{slip_data['customer_name']}\n({slip_data['customer_address']})")
            
            sv_list = [f"- {s[1]} ({s[2]:,}đ)" for s in slip_data["services"]]
            sv_val_lbl.configure(text="\n".join(sv_list))
            
            total_sum = sum(s[2] for s in slip_data["services"])
            price_val_lbl.configure(text=f"{total_sum:,} đ")
            
            # Check if invoice already exists
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MaHD, TrangThai FROM HoaDon WHERE MaPhieu = ?;", (s_id,))
            inv = cursor.fetchone()
            conn.close()
            
            if inv:
                active_invoice_id[0] = inv[0]
                id_lbl.configure(text=f"Mã: {inv[0]}")
                if inv[1] == "DaThanhToan":
                    status_val_lbl.configure(text="Đã thanh toán", fg="green")
                else:
                    status_val_lbl.configure(text="Chưa thanh toán", fg="orange")
            else:
                active_invoice_id[0] = None
                id_lbl.configure(text="Hóa đơn chưa được lưu (Tự tạo mới)")
                status_val_lbl.configure(text="Chưa thanh toán", fg="orange")
                
        slip_combo.bind("<<ComboboxSelected>>", on_slip_selected)
        
        # Actions
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(side="bottom", fill="x", pady=(15, 0))
        
        cancel_btn = tk.Button(
            btn_frame, text="Hủy bỏ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666",
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=15, pady=6, cursor="hand2",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        def confirm_payment():
            selected_str = slip_combo.get()
            if not selected_str:
                messagebox.showerror("Lỗi", "Vui lòng chọn phiếu sửa chữa!", parent=dialog)
                return
                
            s_id = int(selected_str.split(" - ")[0])
            pm_method = "ChuyenKhoan" if method_combo.get() == "Chuyển khoản" else "TienMat"
            
            # Find sum
            slip_data = next((s for s in slips if s["id"] == s_id), None)
            total_sum = sum(s[2] for s in slip_data["services"])
            
            try:
                # If invoice doesn't exist, we must create it first, but db.pay_invoice handles checking if it exists.
                # Let's ensure invoice exists:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT MaHD, TrangThai FROM HoaDon WHERE MaPhieu = ?;", (s_id,))
                inv = cursor.fetchone()
                if not inv:
                    cursor.execute(
                        "INSERT INTO HoaDon (MaPhieu, TongTien, TrangThai) VALUES (?, ?, 'ChuaThanhToan');",
                        (s_id, total_sum)
                    )
                    conn.commit()
                    cursor.execute("SELECT MaHD FROM HoaDon WHERE MaPhieu = ?;", (s_id,))
                    inv_id = cursor.fetchone()[0]
                else:
                    inv_id = inv[0]
                    if inv[1] == "DaThanhToan":
                        messagebox.showwarning("Đã thanh toán", "Hóa đơn của phiếu này đã thanh toán xong!", parent=dialog)
                        conn.close()
                        return
                conn.close()
                
                db.pay_invoice(inv_id, pm_method, self.current_user["id"])
                messagebox.showinfo("Thành công", f"Đã thu tiền và thanh toán hóa đơn #{inv_id} thành công!", parent=dialog)
                dialog.destroy()
                self.refresh_invoices_table()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu thanh toán:\n{e}", parent=dialog)
                
        save_btn = tk.Button(
            btn_frame, 
            text="Xác nhận lưu", 
            bg=ui_helpers.COLOR_PRIMARY_DARK, 
            fg=ui_helpers.COLOR_WHITE, 
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, 
            activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, 
            relief="flat", 
            font=("Arial", 9, "bold"), 
            padx=15, 
            pady=6,
            cursor="hand2",
            command=confirm_payment
        )
        save_btn.pack(side="right", padx=5)
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        # Trigger combobox initial load if there's an option
        if slip_options:
            slip_combo.current(0)
            on_slip_selected(None)

    # ==========================================
    # MANAGER VIEWS
    # ==========================================

    def load_manager_dashboard(self):
        self.clear_view_frame()
        
        # 1. Statistics Cards Row (Top row: 3 cards)
        stats = db.get_stats_today()
        
        stats_frame = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Card 1: Vehicles repaired today
        c1 = tk.Frame(stats_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        c1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(c1, text="SỐ XE SỬA HÔM NAY", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        tk.Label(c1, text=f"{stats['vehicles']} xe", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 20, "bold")).pack(pady=(0, 15))
        
        # Card 2: Revenue today
        c2 = tk.Frame(stats_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        c2.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(c2, text="DOANH THU HÔM NAY", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        tk.Label(c2, text=f"{stats['revenue']:,} đ", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_ACCENT_GOLD, font=("Arial", 20, "bold")).pack(pady=(0, 15))
        
        # Card 3: Popular service today
        c3 = tk.Frame(stats_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        c3.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(c3, text="DỊCH VỤ PHỔ BIẾN HÔM NAY", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        tk.Label(c3, text=stats['popular_service'], bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_ACTIVE_HOVER, font=("Arial", 14, "bold"), wraplength=200, justify="center").pack(pady=(0, 15))
        
        # 2. Charts section (Middle row: 2 charts)
        charts_frame = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        charts_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left chart panel: Pie Chart
        left_chart = tk.Frame(charts_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        left_chart.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right chart panel: Line Chart
        right_chart = tk.Frame(charts_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        right_chart.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Draw Pie Chart (Proportions in 1 quarter)
        dist = db.get_category_distribution_last_quarter()
        fig1, ax1 = plt.subplots(figsize=(4.5, 3), dpi=100)
        fig1.patch.set_facecolor('white')
        if dist:
            labels = [d[0] for d in dist]
            sizes = [d[1] for d in dist]
            colors = [ui_helpers.COLOR_PRIMARY_DARK, ui_helpers.COLOR_ACCENT_LIGHT, ui_helpers.COLOR_ACTIVE_HOVER, ui_helpers.COLOR_ACCENT_GOLD]
            # Draw slices with percentages only, no text labels directly on the pie to prevent cutoff
            wedges, texts, autotexts = ax1.pie(
                sizes, 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=colors[:len(sizes)],
                textprops=dict(color="w", weight="bold")
            )
            ax1.axis('equal')
            
            # Shorten labels in legend if they are too long to prevent cutoff
            short_labels = [l if len(l) <= 22 else l[:20] + "..." for l in labels]
            ax1.legend(wedges, short_labels, title="Danh mục", loc="center left", bbox_to_anchor=(0.95, 0.5), fontsize=8)
            fig1.subplots_adjust(left=0.05, right=0.65, top=0.85, bottom=0.05)
        else:
            ax1.text(0.5, 0.5, "Không có dữ liệu", horizontalalignment='center', verticalalignment='center')
        ax1.set_title("Tỉ trọng dịch vụ quý này", fontsize=10, fontweight='bold', color=ui_helpers.COLOR_PRIMARY_DARK)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=left_chart)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        plt.close(fig1)
        
        # Draw Line Chart (Monthly Revenue)
        m_rev = db.get_monthly_revenue()
        fig2, ax2 = plt.subplots(figsize=(4.5, 3), dpi=100)
        fig2.patch.set_facecolor('white')
        if m_rev:
            months = [m[0] for m in m_rev]
            revenues = [m[1] for m in m_rev]
            ax2.plot(months, revenues, marker='o', color=ui_helpers.COLOR_ACTIVE_HOVER, linewidth=2)
            ax2.grid(True, linestyle='--', alpha=0.5)
            # Format y-axis in thousands
            ax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        else:
            ax2.text(0.5, 0.5, "Không có dữ liệu", horizontalalignment='center', verticalalignment='center')
        ax2.set_title("Doanh thu 6 tháng qua (VND)", fontsize=10, fontweight='bold', color=ui_helpers.COLOR_PRIMARY_DARK)
        ax2.tick_params(axis='x', rotation=15, labelsize=8)
        ax2.tick_params(axis='y', labelsize=8)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=right_chart)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        plt.close(fig2)
        
        # 3. Rankings Row (Bottom row)
        rankings_frame = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT, height=180)
        rankings_frame.pack(fill="x", side="bottom")
        rankings_frame.pack_propagate(False)
        
        # Top Staff List
        top_staff_frame = tk.Frame(rankings_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        top_staff_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(top_staff_frame, text="TOP NHÂN VIÊN CHĂM CHỈ (NHIỀU HOẠT ĐỘNG)", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=5)
        
        staff_list = db.get_top_staff()
        for idx, (name, count) in enumerate(staff_list):
            lbl_text = f" {idx+1}. {name} - {count} hoạt động"
            tk.Label(top_staff_frame, text=lbl_text, bg=ui_helpers.COLOR_WHITE, fg="#333333", font=("Arial", 9)).pack(anchor="w", padx=20, pady=2)
            
        # Top Customers List
        top_cust_frame = tk.Frame(rankings_frame, bg=ui_helpers.COLOR_WHITE, bd=1, relief="solid", highlightbackground=ui_helpers.COLOR_ACCENT_LIGHT, highlightthickness=0)
        top_cust_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(top_cust_frame, text="TOP KHÁCH HÀNG THÂN THIẾT (QUAY LẠI)", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=5)
        
        cust_list = db.get_top_customers()
        for idx, (name, count) in enumerate(cust_list):
            lbl_text = f" {idx+1}. {name} - {count} phiếu sửa chữa"
            tk.Label(top_cust_frame, text=lbl_text, bg=ui_helpers.COLOR_WHITE, fg="#333333", font=("Arial", 9)).pack(anchor="w", padx=20, pady=2)

    def load_manager_services(self):
        self.clear_view_frame()
        
        # Header bar above divider line
        header_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        header_bar.pack(fill="x", pady=(0, 10))
        
        # Left search / filter
        left_filters = tk.Frame(header_bar, bg=ui_helpers.COLOR_BG_LIGHT)
        left_filters.pack(side="left")
        
        tk.Label(left_filters, text="Dịch vụ: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold")).pack(side="left")
        search_entry = ui_helpers.CustomEntry(left_filters, width=200)
        search_entry.pack(side="left", padx=5)
        
        tk.Label(left_filters, text=" Lọc loại: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold")).pack(side="left")
        
        # Load categories
        cats = db.get_categories()
        cat_choices = ["Tất cả"] + [c[1] for c in cats]
        cat_filter_combo = ttk.Combobox(left_filters, values=cat_choices, state="readonly", width=15, font=("Arial", 10))
        cat_filter_combo.pack(side="left", padx=5)
        cat_filter_combo.current(0)
        
        # Right action buttons (3 buttons in different colors)
        right_actions = tk.Frame(header_bar, bg=ui_helpers.COLOR_BG_LIGHT)
        right_actions.pack(side="right")
        
        btn_cat = tk.Button(
            right_actions, text=" + Thêm Phân Loại", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE,
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=10, pady=6, cursor="hand2",
            command=self.open_add_category_dialog
        )
        btn_cat.pack(side="left", padx=3)
        btn_cat.bind("<Enter>", lambda e: btn_cat.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        btn_cat.bind("<Leave>", lambda e: btn_cat.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        btn_service = tk.Button(
            right_actions, text=" + Thêm Dịch Vụ", bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE,
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=10, pady=6, cursor="hand2",
            command=self.open_add_service_dialog
        )
        btn_service.pack(side="left", padx=3)
        btn_service.bind("<Enter>", lambda e: btn_service.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        btn_service.bind("<Leave>", lambda e: btn_service.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        
        btn_price = tk.Button(
            right_actions, text=" Set Giá Dịch Vụ", bg=ui_helpers.COLOR_ACCENT_GOLD, fg="#2C3E35",
            activebackground=ui_helpers.COLOR_ACTIVE_HOVER, activeforeground=ui_helpers.COLOR_WHITE,
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=10, pady=6, cursor="hand2",
            command=self.open_set_price_dialog
        )
        btn_price.pack(side="left", padx=3)
        btn_price.bind("<Enter>", lambda e: btn_price.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
        btn_price.bind("<Leave>", lambda e: btn_price.configure(bg=ui_helpers.COLOR_ACCENT_GOLD, fg="#2C3E35"))
        
        # Faint line divider
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # Scrollable grid matching database structure <phân loại-dịch vụ-giá cả-thao tác>
        # Headers: 150px, 250px, 120px, 180px
        self.services_table = ui_helpers.ScrollableTable(
            self.view_frame, 
            headers=["Phân loại dịch vụ", "Tên dịch vụ cụ thể", "Đơn giá (VND)", "Thao tác"],
            col_widths=[180, 280, 150, 200]
        )
        self.services_table.pack(fill="both", expand=True)
        
        # Load services helper
        def refresh_services_grid(*args):
            self.services_table.clear()
            
            # Get filter inputs
            q = search_entry.get().strip()
            cat_selected = cat_filter_combo.get()
            
            cat_id = None
            if cat_selected != "Tất cả":
                cat_match = next((c for c in cats if c[1] == cat_selected), None)
                if cat_match:
                    cat_id = cat_match[0]
                    
            rows = db.get_services(category_id=cat_id, search_query=q)
            
            for r in rows:
                # r is (MaDV, MaLoai, TenLoai, TenDichVu, Gia)
                price_str = f"{r[4]:,} đ"
                
                # We need to specify the action buttons in the cell creator closure
                def create_actions(frame, bg_c, service_data=r):
                    # Update (Cập nhật) button
                    upd_btn = tk.Button(
                        frame, text="Sửa", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
                        bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                        command=lambda: self.open_update_service_dialog(service_data)
                    )
                    upd_btn.pack(side="left", padx=5, pady=5)
                    upd_btn.bind("<Enter>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    upd_btn.bind("<Leave>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35"))
                    
                    # Delete (Xóa) button
                    del_btn = tk.Button(
                        frame, text="Xóa", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED,
                        bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                        command=lambda: self.confirm_delete_service(service_data[0])
                    )
                    del_btn.pack(side="left", padx=5, pady=5)
                    del_btn.bind("<Enter>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    del_btn.bind("<Leave>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED))

                self.services_table.add_row(
                    values=[r[2], r[3], price_str], 
                    action_creator=create_actions
                )
                
        # Binds
        search_entry.entry.bind("<Return>", refresh_services_grid)
        cat_filter_combo.bind("<<ComboboxSelected>>", refresh_services_grid)
        
        # Initial load
        refresh_services_grid()

    def confirm_delete_service(self, service_id):
        confirm = messagebox.askyesno("Xóa dịch vụ", "Bạn có chắc chắn muốn xóa dịch vụ này khỏi hệ thống?")
        if confirm:
            try:
                db.delete_service(service_id, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã xóa dịch vụ thành công!")
                self.load_manager_services()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa dịch vụ:\n{e}")

    def open_add_category_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm Phân Loại Dịch Vụ")
        dialog.geometry("380x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 380, 250)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="THÊM PHÂN LOẠI DỊCH VỤ", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 20))
        
        tk.Label(form_frame, text="Tên phân loại *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        cat_entry = ui_helpers.CustomEntry(form_frame)
        cat_entry.pack(fill="x", pady=(0, 20))
        
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def save():
            name = cat_entry.get().strip()
            if not name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên phân loại!", parent=dialog)
                return
            try:
                db.add_category(name, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã lưu phân loại mới thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_services()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Lưu", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=save, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def open_add_service_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thêm Dịch Vụ Mới")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 400, 320)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="THÊM DỊCH VỤ SỬA CHỮA MỚI", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Category Dropdown
        tk.Label(form_frame, text="Chọn phân loại dịch vụ *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        cats = db.get_categories()
        cat_choices = [c[1] for c in cats]
        cat_combo = ttk.Combobox(form_frame, values=cat_choices, state="readonly", font=("Arial", 10))
        cat_combo.pack(fill="x", pady=(0, 10))
        if cat_choices:
            cat_combo.current(0)
            
        # Service name Textbox
        tk.Label(form_frame, text="Tên dịch vụ sửa chữa *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        service_entry = ui_helpers.CustomEntry(form_frame)
        service_entry.pack(fill="x", pady=(0, 20))
        
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def save():
            cat_name = cat_combo.get()
            sv_name = service_entry.get().strip()
            if not cat_name:
                messagebox.showerror("Lỗi", "Vui lòng chọn phân loại dịch vụ!", parent=dialog)
                return
            if not sv_name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên dịch vụ!", parent=dialog)
                return
                
            cat_id = next(c[0] for c in cats if c[1] == cat_name)
            try:
                db.add_service(cat_id, sv_name, 0, self.current_user["id"]) # Price 0 initially, updated using Set Price
                messagebox.showinfo("Thành công", "Đã tạo dịch vụ mới. Vui lòng sử dụng tính năng Set Giá để cập nhật đơn giá dịch vụ!", parent=dialog)
                dialog.destroy()
                self.load_manager_services()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Lưu dịch vụ", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=save, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def open_set_price_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Thiết Lập Đơn Giá Dịch Vụ")
        dialog.geometry("400x380")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 400, 380)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="THIẾT LẬP GIÁ CẢ DỊCH VỰ", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 15))
        
        cats = db.get_categories()
        cat_choices = [c[1] for c in cats]
        
        # Categorized service loading logic
        tk.Label(form_frame, text="Phân loại dịch vụ:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        cat_combo = ttk.Combobox(form_frame, values=cat_choices, state="readonly", font=("Arial", 10))
        cat_combo.pack(fill="x", pady=(0, 10))
        
        tk.Label(form_frame, text="Dịch vụ cụ thể *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        service_combo = ttk.Combobox(form_frame, state="readonly", font=("Arial", 10))
        service_combo.pack(fill="x", pady=(0, 10))
        
        # Price input
        tk.Label(form_frame, text="Đơn giá (VND) *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        price_entry = ui_helpers.CustomEntry(form_frame)
        price_entry.pack(fill="x", pady=(0, 20))
        
        services_map = [None] # closure storage
        
        def load_services_for_cat(event=None):
            cat_name = cat_combo.get()
            if not cat_name:
                return
            cat_id = next(c[0] for c in cats if c[1] == cat_name)
            services = db.get_services(category_id=cat_id)
            services_map[0] = services
            
            names = [s[3] for s in services]
            service_combo.configure(values=names)
            if names:
                service_combo.current(0)
                # prefill current price
                price_entry.delete(0, tk.END)
                price_entry.insert(0, str(services[0][4]))
            else:
                service_combo.set("")
                price_entry.delete(0, tk.END)
                
        def on_service_selected(event=None):
            idx = service_combo.current()
            if idx >= 0 and services_map[0]:
                price_entry.delete(0, tk.END)
                price_entry.insert(0, str(services_map[0][idx][4]))
                
        cat_combo.bind("<<ComboboxSelected>>", load_services_for_cat)
        service_combo.bind("<<ComboboxSelected>>", on_service_selected)
        
        if cat_choices:
            cat_combo.current(0)
            load_services_for_cat()
            
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def save():
            idx = service_combo.current()
            if idx < 0 or not services_map[0]:
                messagebox.showerror("Lỗi", "Vui lòng chọn dịch vụ!", parent=dialog)
                return
            try:
                price = int(price_entry.get().strip())
                if price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập đơn giá hợp lệ (Số nguyên dương)!", parent=dialog)
                return
                
            sv_id = services_map[0][idx][0]
            sv_name = services_map[0][idx][3]
            cat_id = services_map[0][idx][1]
            try:
                db.update_service(sv_id, cat_id, sv_name, price, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã thiết lập đơn giá mới thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_services()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Lưu giá cả", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=save, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def open_update_service_dialog(self, service_data):
        # service_data is (MaDV, MaLoai, TenLoai, TenDichVu, Gia)
        dialog = tk.Toplevel(self)
        dialog.title("Cập nhật Dịch Vụ")
        dialog.geometry("400x380")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 400, 380)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="CẬP NHẬT DỊCH VỤ SỬA CHỮA", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Category Dropdown
        tk.Label(form_frame, text="Phân loại dịch vụ *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        cats = db.get_categories()
        cat_choices = [c[1] for c in cats]
        cat_combo = ttk.Combobox(form_frame, values=cat_choices, state="readonly", font=("Arial", 10))
        cat_combo.pack(fill="x", pady=(0, 10))
        
        # Find index and select
        curr_cat_name = service_data[2]
        if curr_cat_name in cat_choices:
            cat_combo.current(cat_choices.index(curr_cat_name))
            
        # Service name
        tk.Label(form_frame, text="Tên dịch vụ sửa chữa *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        service_entry = ui_helpers.CustomEntry(form_frame)
        service_entry.pack(fill="x", pady=(0, 10))
        service_entry.insert(0, service_data[3])
        
        # Price
        tk.Label(form_frame, text="Đơn giá (VND) *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        price_entry = ui_helpers.CustomEntry(form_frame)
        price_entry.pack(fill="x", pady=(0, 20))
        price_entry.insert(0, str(service_data[4]))
        
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def update():
            cat_name = cat_combo.get()
            sv_name = service_entry.get().strip()
            
            if not cat_name or not sv_name:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!", parent=dialog)
                return
                
            try:
                price = int(price_entry.get().strip())
                if price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập đơn giá hợp lệ!", parent=dialog)
                return
                
            cat_id = next(c[0] for c in cats if c[1] == cat_name)
            try:
                db.update_service(service_data[0], cat_id, sv_name, price, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã cập nhật dịch vụ thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_services()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Cập nhật", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=update, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def load_manager_staff(self):
        self.clear_view_frame()
        
        top_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        top_bar.pack(fill="x", pady=(0, 10))
        
        tk.Label(top_bar, text="Tìm nhân viên: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        search_entry = ui_helpers.CustomEntry(top_bar, width=300)
        search_entry.pack(side="left", fill="y", padx=5)
        
        add_btn = tk.Button(
            top_bar, text=" + Tạo Tài Khoản Nhân Viên", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE,
            bd=0, relief="flat", font=("Arial", 10, "bold"), padx=15, pady=8, cursor="hand2",
            command=self.open_add_staff_dialog
        )
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
        
        # Divider Line
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # ScrollableTable <id- tên nhân viên- đăng nhập- mật khẩu- thao tác(cập nhật và xóa)>
        self.staff_table = ui_helpers.ScrollableTable(
            self.view_frame,
            headers=["ID", "Họ và tên nhân viên", "Tên đăng nhập", "Mật khẩu", "Vai trò", "Thao tác"],
            col_widths=[80, 250, 150, 150, 120, 200]
        )
        self.staff_table.pack(fill="both", expand=True)
        
        def refresh_staff_grid():
            self.staff_table.clear()
            q = search_entry.get().strip()
            rows = db.get_staff(q)
            for r in rows:
                # r: (MaNV, HoTen, TenDangNhap, MatKhau, VaiTro)
                role_str = "Quản lý" if r[4] == "QuanLy" else "Nhân viên"
                
                def create_actions(frame, bg_c, staff_data=r):
                    upd_btn = tk.Button(
                        frame, text="Cập nhật", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
                        bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                        command=lambda: self.open_update_staff_dialog(staff_data)
                    )
                    upd_btn.pack(side="left", padx=5, pady=5)
                    upd_btn.bind("<Enter>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    upd_btn.bind("<Leave>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35"))
                    
                    # Cannot delete oneself
                    if staff_data[0] != self.current_user["id"]:
                        del_btn = tk.Button(
                            frame, text="Xóa", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED,
                            bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                            command=lambda: self.confirm_delete_staff(staff_data[0])
                        )
                        del_btn.pack(side="left", padx=5, pady=5)
                        del_btn.bind("<Enter>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                        del_btn.bind("<Leave>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED))

                self.staff_table.add_row(
                    values=[r[0], r[1], r[2], r[3], role_str],
                    action_creator=create_actions
                )
                
        search_entry.entry.bind("<Return>", lambda e: refresh_staff_grid())
        refresh_staff_grid()

    def confirm_delete_staff(self, staff_id):
        confirm = messagebox.askyesno("Xóa tài khoản", "Bạn có chắc chắn muốn xóa tài khoản nhân viên này?")
        if confirm:
            try:
                db.delete_staff(staff_id, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã xóa tài khoản thành công!")
                self.load_manager_staff()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên:\n{e}")

    def open_add_staff_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Tạo Tài Khoản Nhân Viên")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 400, 400)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="THÔNG TIN TÀI KHOẢN MỚI", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Name
        tk.Label(form_frame, text="Họ và tên nhân viên *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        name_entry = ui_helpers.CustomEntry(form_frame)
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Username
        tk.Label(form_frame, text="Tên đăng nhập *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        user_entry = ui_helpers.CustomEntry(form_frame)
        user_entry.pack(fill="x", pady=(0, 10))
        
        # Password
        tk.Label(form_frame, text="Mật khẩu *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        pass_entry = ui_helpers.CustomEntry(form_frame)
        pass_entry.pack(fill="x", pady=(0, 10))
        
        # Role
        tk.Label(form_frame, text="Vai trò hệ thống *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        role_combo = ttk.Combobox(form_frame, values=["Nhân viên", "Quản lý"], state="readonly", font=("Arial", 10))
        role_combo.pack(fill="x", pady=(0, 20))
        role_combo.current(0)
        
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def save():
            name = name_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            role = "QuanLy" if role_combo.get() == "Quản lý" else "NhanVien"
            
            if not name or not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=dialog)
                return
                
            try:
                db.add_staff(name, username, password, role, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã tạo tài khoản nhân viên thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_staff()
            except sqlite3.IntegrityError:
                messagebox.showerror("Trùng tên đăng nhập", "Tên đăng nhập đã tồn tại trong hệ thống!", parent=dialog)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Tạo tài khoản", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=save, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def open_update_staff_dialog(self, staff_data):
        # staff_data: (MaNV, HoTen, TenDangNhap, MatKhau, VaiTro)
        dialog = tk.Toplevel(self)
        dialog.title("Cập Nhật Nhân Viên")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 400, 400)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="THÔNG TIN TÀI KHOẢN NHÂN VIÊN", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Name
        tk.Label(form_frame, text="Họ và tên nhân viên *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        name_entry = ui_helpers.CustomEntry(form_frame)
        name_entry.pack(fill="x", pady=(0, 10))
        name_entry.insert(0, staff_data[1])
        
        # Username
        tk.Label(form_frame, text="Tên đăng nhập *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        user_entry = ui_helpers.CustomEntry(form_frame)
        user_entry.pack(fill="x", pady=(0, 10))
        user_entry.insert(0, staff_data[2])
        
        # Password
        tk.Label(form_frame, text="Mật khẩu *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        pass_entry = ui_helpers.CustomEntry(form_frame)
        pass_entry.pack(fill="x", pady=(0, 10))
        pass_entry.insert(0, staff_data[3])
        
        # Role
        tk.Label(form_frame, text="Vai trò hệ thống *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        role_combo = ttk.Combobox(form_frame, values=["Nhân viên", "Quản lý"], state="readonly", font=("Arial", 10))
        role_combo.pack(fill="x", pady=(0, 20))
        
        # Prevent active user from changing their own role to something else
        if staff_data[0] == self.current_user["id"]:
            role_combo.configure(state="disabled")
            
        role_combo.current(1 if staff_data[4] == "QuanLy" else 0)
        
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(fill="x", side="bottom")
        
        cancel = tk.Button(btn_frame, text="Hủy", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666", bd=0, padx=15, pady=5, command=dialog.destroy, cursor="hand2")
        cancel.pack(side="left")
        
        def save():
            name = name_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            role = "QuanLy" if role_combo.get() == "Quản lý" else "NhanVien"
            
            if not name or not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=dialog)
                return
                
            try:
                db.update_staff(staff_data[0], name, username, password, role, self.current_user["id"])
                # If active user edited their own name, refresh display session
                if staff_data[0] == self.current_user["id"]:
                    self.current_user["name"] = name
                    self.header_user.configure(text=f"{name} (Quản lý)")
                messagebox.showinfo("Thành công", "Đã cập nhật tài khoản thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_staff()
            except sqlite3.IntegrityError:
                messagebox.showerror("Trùng tên đăng nhập", "Tên đăng nhập đã tồn tại trong hệ thống!", parent=dialog)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống:\n{e}", parent=dialog)
                
        save_btn = tk.Button(btn_frame, text="Lưu thay đổi", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE, bd=0, padx=15, pady=5, command=save, cursor="hand2")
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

    def load_manager_invoices(self):
        self.clear_view_frame()
        
        top_bar = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_BG_LIGHT)
        top_bar.pack(fill="x", pady=(0, 10))
        
        tk.Label(top_bar, text="Tìm kiếm hóa đơn: ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#333333", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        search_entry = ui_helpers.CustomEntry(top_bar, width=300)
        search_entry.pack(side="left", fill="y", padx=5)
        
        # Divider Line
        divider = tk.Frame(self.view_frame, bg=ui_helpers.COLOR_ACCENT_LIGHT, height=1)
        divider.pack(fill="x", padx=40, pady=15)
        
        # ScrollableTable <id hóa đơn- tên khách hàng- loại dịch vụ- giá tiền- trạng thái- ngày thanh toán- thao tác(pdf, xóa)>
        self.m_invoice_table = ui_helpers.ScrollableTable(
            self.view_frame,
            headers=["Mã HĐ", "Họ tên khách hàng", "Chi tiết dịch vụ thực hiện", "Tổng cộng (VND)", "Trạng thái", "Ngày thanh toán", "Thao tác"],
            col_widths=[70, 160, 250, 120, 120, 140, 185]
        )
        self.m_invoice_table.pack(fill="both", expand=True)
        
        def refresh_invoices():
            self.m_invoice_table.clear()
            q = search_entry.get().strip()
            rows = db.get_invoices(q)
            
            for r in rows:
                st_str = "Đã thanh toán" if r["status"] == "DaThanhToan" else "Chưa thanh toán"
                pm_date = r["payment_date"] if r["payment_date"] else "N/A"
                
                # Combine category and service names
                # r["services"] is list of (TenDichVu, DonGia, TenLoai)
                sv_summary = ", ".join([f"{s[2]}: {s[0]}" for s in r["services"]])
                if len(sv_summary) > 40:
                    sv_summary = sv_summary[:37] + "..."
                    
                price_str = f"{r['total_amount']:,}đ"
                
                def create_actions(frame, bg_c, inv_data=r):
                    pdf_btn = tk.Button(
                        frame, text="Xuất PDF ⎙", bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE,
                        bd=0, font=("Arial", 8, "bold"), padx=8, pady=2, cursor="hand2",
                        command=lambda: self.export_invoice_pdf(inv_data)
                    )
                    pdf_btn.pack(side="left", padx=3, pady=5)
                    pdf_btn.bind("<Enter>", lambda e: pdf_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))
                    pdf_btn.bind("<Leave>", lambda e: pdf_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
                    
                    del_btn = tk.Button(
                        frame, text="Xóa", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED,
                        bd=0, font=("Arial", 8, "bold"), padx=8, pady=2, cursor="hand2",
                        command=lambda: self.confirm_delete_invoice(inv_data["id"])
                    )
                    del_btn.pack(side="left", padx=3, pady=5)
                    del_btn.bind("<Enter>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    del_btn.bind("<Leave>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED))

                self.m_invoice_table.add_row(
                    values=[r["id"], r["customer_name"], sv_summary, price_str, st_str, pm_date],
                    action_creator=create_actions
                )
                
        search_entry.entry.bind("<Return>", lambda e: refresh_invoices())
        refresh_invoices()

    def export_invoice_pdf(self, inv):
        # Generate Invoice PDF under D:\project_py\invoice_{id}.pdf
        try:
            pdf_path = f"D:\\project_py\\invoice_{inv['id']}.pdf"
            
            pdf = FPDF()
            pdf.add_page()
            
            # Load Vietnamese fonts from Windows system font folder
            font_path = r"C:\Windows\Fonts\segoeui.ttf"
            font_bold_path = r"C:\Windows\Fonts\segoeuib.ttf"
            font_italic_path = r"C:\Windows\Fonts\segoeuii.ttf"
            
            if os.path.exists(font_path) and os.path.exists(font_bold_path) and os.path.exists(font_italic_path):
                pdf.add_font("SegoeUI", "", font_path)
                pdf.add_font("SegoeUI", "B", font_bold_path)
                pdf.add_font("SegoeUI", "I", font_italic_path)
                pdf.set_font("SegoeUI", size=11)
                font_name = "SegoeUI"
            else:
                pdf.set_font("Helvetica", size=11)
                font_name = "Helvetica"
                
            # Content
            # 1. Title/Header
            pdf.set_font(font_name, "B", 16)
            pdf.cell(w=0, h=10, text="TRUNG TÂM DỊCH VỤ & SỬA CHỮA XE", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.set_font(font_name, "", 10)
            pdf.cell(w=0, h=5, text="Địa chỉ: 470 Trần Đại Nghĩa - quận Ngũ Hành Sơn - tp Đà Nẵng", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.cell(w=0, h=5, text="Hotline: 0987.654.321 - Email: contact@garage.vn", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(10)
            
            # 2. Invoice Details
            pdf.set_font(font_name, "B", 14)
            pdf.cell(w=0, h=10, text=f"HÓA ĐƠN THANH TOÁN #HĐ-{inv['id']}", new_x="LMARGIN", new_y="NEXT", align="L")
            pdf.set_font(font_name, "", 10)
            pdf.line(10, 42, 200, 42)
            pdf.ln(5)
            
            pdf.cell(w=50, h=6, text="Mã phiếu sửa chữa:")
            pdf.cell(w=0, h=6, text=f"P-{inv['slip_id']} ({inv['slip_name']})", new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(w=50, h=6, text="Họ tên khách hàng:")
            pdf.cell(w=0, h=6, text=inv["customer_name"], new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(w=50, h=6, text="Địa chỉ khách hàng:")
            pdf.cell(w=0, h=6, text=inv["customer_address"], new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(w=50, h=6, text="Ngày thanh toán:")
            pdf.cell(w=0, h=6, text=inv["payment_date"] if inv["payment_date"] else "Chưa thanh toán", new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(w=50, h=6, text="Phương thức:")
            pm = "Chuyển khoản" if inv["payment_method"] == "ChuyenKhoan" else ("Tiền mặt" if inv["payment_method"] == "TienMat" else "N/A")
            pdf.cell(w=0, h=6, text=pm, new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(w=50, h=6, text="Trạng thái:")
            st = "ĐÃ THANH TOÁN" if inv["status"] == "DaThanhToan" else "CHƯA THANH TOÁN"
            pdf.cell(w=0, h=6, text=st, new_x="LMARGIN", new_y="NEXT")
            
            # Helper to wrap text into lines fitting a specific width
            def get_wrapped_lines(text, width):
                words = str(text).split(" ")
                lines = []
                current_line = ""
                for word in words:
                    test_line = f"{current_line} {word}".strip() if current_line else word
                    if pdf.get_string_width(test_line) <= (width - 4): # 4mm padding
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                return lines

            pdf.ln(8)
            
            # 3. Services Table
            pdf.set_font(font_name, "B", 11)
            pdf.cell(w=10, h=8, text="STT", border=1, align="C")
            pdf.cell(w=100, h=8, text="Dịch vụ sửa chữa", border=1, align="L")
            pdf.cell(w=40, h=8, text="Phân loại", border=1, align="L")
            pdf.cell(w=40, h=8, text="Đơn giá (VND)", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font(font_name, "", 10)
            total_price = 0
            line_height = 5
            
            for idx, sv in enumerate(inv["services"]):
                stt_text = str(idx+1)
                service_text = sv[0]
                category_text = sv[2]
                price_text = f"{sv[1]:,}"
                
                # Wrap columns
                col1_lines = [stt_text]
                col2_lines = get_wrapped_lines(service_text, 100)
                col3_lines = get_wrapped_lines(category_text, 40)
                col4_lines = [price_text]
                
                max_lines = max(len(col1_lines), len(col2_lines), len(col3_lines), len(col4_lines))
                row_height = max_lines * line_height + 4 # 4mm padding for height
                
                col_widths = [10, 100, 40, 40]
                col_contents = [col1_lines, col2_lines, col3_lines, col4_lines]
                col_aligns = ["C", "L", "L", "R"]
                
                current_x = pdf.get_x()
                current_y = pdf.get_y()
                
                # Draw column by column
                for w, contents, align in zip(col_widths, col_contents, col_aligns):
                    # Draw cell border rectangle
                    pdf.rect(current_x, current_y, w, row_height)
                    
                    # Compute starting y to vertically center text
                    text_height = len(contents) * line_height
                    offset_y = (row_height - text_height) / 2
                    
                    # Print lines
                    for i, line in enumerate(contents):
                        pdf.set_xy(current_x, current_y + offset_y + i * line_height)
                        pdf.cell(w=w, h=line_height, text=line, border=0, align=align)
                        
                    current_x += w
                
                # Move to next row
                pdf.set_xy(10, current_y + row_height)
                total_price += sv[1]
                
            pdf.set_font(font_name, "B", 11)
            pdf.cell(w=150, h=8, text="TỔNG CỘNG:", border=1, align="R")
            pdf.cell(w=40, h=8, text=f"{total_price:,} đ", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(15)
            
            # 4. Signatures
            pdf.set_font(font_name, "I", 10)
            pdf.cell(w=95, h=5, text="Khách hàng ký nhận", align="C")
            pdf.cell(w=95, h=5, text="Nhân viên thu ngân", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(w=95, h=5, text="(Ký, ghi rõ họ tên)", align="C")
            pdf.cell(w=95, h=5, text="(Ký, ghi rõ họ tên)", align="C", new_x="LMARGIN", new_y="NEXT")
            
            pdf.output(pdf_path)
            
            # Show success message and auto-open PDF on Windows
            messagebox.showinfo("Xuất PDF thành công", f"Đã xuất hóa đơn PDF thành công tại:\n{pdf_path}")
            
            if sys.platform == "win32":
                os.startfile(pdf_path)
                
            db.log_action(self.current_user["id"], f"Xuất hóa đơn PDF ID: {inv['id']}")
            
        except Exception as e:
            messagebox.showerror("Lỗi PDF", f"Không thể xuất file PDF:\n{e}")

    def confirm_delete_invoice(self, hd_id):
        confirm = messagebox.askyesno(
            "Xóa hóa đơn", 
            "Bạn có chắc chắn muốn xóa hóa đơn này (và phiếu sửa chữa tương ứng) do khách hàng không thanh toán đúng hạn?",
            parent=self
        )
        if confirm:
            try:
                db.delete_invoice(hd_id, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã xóa hóa đơn thành công!", parent=self)
                self.load_manager_invoices()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa hóa đơn:\n{e}", parent=self)

    def load_manager_customer_care(self):
        self.clear_view_frame()
        
        # Display table `<tên phiếu - tên khách hàng - sđt - dịch vụ - tính chất - thao tác>` loaded from PhieuSuaChua
        self.care_table = ui_helpers.ScrollableTable(
            self.view_frame,
            headers=["Tên phiếu sửa chữa", "Họ tên khách hàng", "Số điện thoại", "Dịch vụ thực hiện", "Tính chất", "Thao tác"],
            col_widths=[140, 160, 110, 200, 120, 150]
        )
        self.care_table.pack(fill="both", expand=True)
        
        def refresh_care_table():
            self.care_table.clear()
            # Fetch slips
            slips = db.get_slips()
            for s in slips:
                sv_summary = ", ".join([s[1] for s in s["services"]])
                if len(sv_summary) > 40:
                    sv_summary = sv_summary[:37] + "..."
                    
                nat_str = "Lấy liền" if s["nature"] == "LayLien" else f"Hẹn: {s['start_date']} -> {s['end_date']}"
                
                def create_actions(frame, bg_c, slip_data=s):
                    # Cập nhật (full edit dialog)
                    upd_btn = tk.Button(
                        frame, text="Cập nhật", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
                        bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                        command=lambda: self.open_create_slip_dialog(slip_data)
                    )
                    upd_btn.pack(side="left", padx=5, pady=5)
                    upd_btn.bind("<Enter>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    upd_btn.bind("<Leave>", lambda e: upd_btn.configure(bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35"))
                    
                    # Xóa button
                    del_btn = tk.Button(
                        frame, text="Xóa", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED,
                        bd=0, font=("Arial", 8, "bold"), padx=10, pady=2, cursor="hand2",
                        command=lambda: self.confirm_delete_slip(slip_data["id"])
                    )
                    del_btn.pack(side="left", padx=5, pady=5)
                    del_btn.bind("<Enter>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER, fg=ui_helpers.COLOR_WHITE))
                    del_btn.bind("<Leave>", lambda e: del_btn.configure(bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_RED))

                self.care_table.add_row(
                    values=[s["title"], s["customer_name"], s["customer_phone"], sv_summary, nat_str],
                    action_creator=create_actions
                )
                
        refresh_care_table()

    def confirm_delete_slip(self, slip_id):
        confirm = messagebox.askyesno("Xóa phiếu sửa chữa", "Bạn có chắc chắn muốn xóa phiếu sửa chữa này và toàn bộ hóa đơn/thanh toán liên quan?", parent=self)
        if confirm:
            try:
                db.delete_slip(slip_id, self.current_user["id"])
                messagebox.showinfo("Thành công", "Đã xóa phiếu sửa chữa thành công!", parent=self)
                if self.current_user["role"] == "QuanLy":
                    self.load_manager_customer_care()
                else:
                    self.load_staff_slips()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa phiếu sửa chữa:\n{e}", parent=self)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa phiếu sửa chữa:\n{e}")

    def open_reschedule_slip_dialog(self, slip):
        # Dialog similar to create slip but prefilled and allows updating dates specifically
        dialog = tk.Toplevel(self)
        dialog.title("Cập Nhật & Điều Chỉnh Lịch Hẹn")
        dialog.geometry("600x650")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        self.center_toplevel(dialog, 600, 650)
        
        form_frame = tk.Frame(dialog, bg=ui_helpers.COLOR_WHITE, padx=25, pady=25)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="CẬP NHẬT PHIẾU / ĐIỀU CHỈNH LỊCH HẸN", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Slip Name
        tk.Label(form_frame, text="Tên phiếu *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        slip_name_entry = ui_helpers.CustomEntry(form_frame)
        slip_name_entry.pack(fill="x", pady=(0, 10))
        slip_name_entry.insert(0, slip["title"])
        
        # Customer Droplist
        tk.Label(form_frame, text="Thông tin khách hàng *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        customers = db.get_customers()
        cust_options = [f"{c[0]} - {c[1]} - {c[3]}" for c in customers]
        
        cust_combo = ttk.Combobox(form_frame, values=cust_options, state="readonly", font=("Arial", 10))
        cust_combo.pack(fill="x", pady=(0, 10))
        
        # Prefill customer
        cust_match = next((opt for opt in cust_options if opt.startswith(f"{slip['customer_id']} - ")), None)
        if cust_match:
            cust_combo.current(cust_options.index(cust_match))
            
        # Services Droplist containing Cascade Menu
        tk.Label(form_frame, text="Dịch vụ sửa chữa * (Chọn thêm dịch vụ từ Menu):", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        # Load active services from slip
        # slip["services"] is list of (MaDV, TenDichVu, DonGia, TenLoai)
        selected_services = []
        for s in slip["services"]:
            selected_services.append((s[0], s[1], s[2], s[3]))
            
        # Container to show selected services
        services_container = tk.LabelFrame(form_frame, text=" Các dịch vụ đã chọn ", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold"))
        services_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollable service area inside container
        sv_canvas = tk.Canvas(services_container, bg=ui_helpers.COLOR_WHITE, highlightthickness=0, height=80)
        sv_scroll = ttk.Scrollbar(services_container, orient="vertical", command=sv_canvas.yview)
        sv_frame = tk.Frame(sv_canvas, bg=ui_helpers.COLOR_WHITE)
        
        sv_frame.bind(
            "<Configure>",
            lambda e: sv_canvas.configure(scrollregion=sv_canvas.bbox("all"))
        )
        sv_canvas.create_window((0,0), window=sv_frame, anchor="nw")
        sv_canvas.configure(yscrollcommand=sv_scroll.set)
        
        sv_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sv_scroll.pack(side="right", fill="y", pady=5)
        
        total_price_lbl = tk.Label(form_frame, text="Tổng cộng tạm tính: 0 đ", bg=ui_helpers.COLOR_WHITE, fg=ui_helpers.COLOR_PRIMARY_DARK, font=("Arial", 10, "bold"))
        total_price_lbl.pack(anchor="e", pady=(0, 5))
        
        def render_selected_services():
            # Clear frame
            for widget in sv_frame.winfo_children():
                widget.destroy()
            
            total = 0
            for idx, sv in enumerate(selected_services):
                row = tk.Frame(sv_frame, bg=ui_helpers.COLOR_WHITE, height=25)
                row.pack(fill="x", pady=2)
                
                lbl_text = f"[{sv[3]}] {sv[1]} - {sv[2]:,}đ"
                lbl = tk.Label(row, text=lbl_text, bg=ui_helpers.COLOR_WHITE, fg="#333333", font=("Arial", 9), anchor="w")
                lbl.pack(side="left", fill="both", expand=True)
                
                del_btn = tk.Button(
                    row, text="✕", bg=ui_helpers.COLOR_WHITE, fg="red", bd=0, font=("Arial", 8, "bold"),
                    command=lambda idx=idx: remove_service(idx), cursor="hand2"
                )
                del_btn.pack(side="right", padx=5)
                
                total += sv[2]
                
            total_price_lbl.configure(text=f"Tổng cộng tạm tính: {total:,} đ")
            
        def remove_service(index):
            selected_services.pop(index)
            render_selected_services()
            
        def add_service_to_list(sv_data):
            if any(s[0] == sv_data[0] for s in selected_services):
                messagebox.showwarning("Lỗi", "Dịch vụ này đã có trong danh sách!", parent=dialog)
                return
            selected_services.append((sv_data[0], sv_data[3], sv_data[4], sv_data[2])) # MaDV, TenDichVu, Gia, TenLoai
            render_selected_services()

        # Cascade Menu builder button
        menu_btn = tk.Button(
            form_frame, text="✚ Chọn phân loại & dịch vụ sửa chữa...", bg=ui_helpers.COLOR_ACCENT_LIGHT, fg="#2C3E35",
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=10, pady=5, cursor="hand2"
        )
        menu_btn.pack(fill="x", pady=(0, 10))
        
        service_menu = tk.Menu(dialog, tearoff=0)
        cats = db.get_categories()
        for c in cats:
            sub_menu = tk.Menu(service_menu, tearoff=0)
            services = db.get_services(category_id=c[0])
            if not services:
                sub_menu.add_command(label="(Trống)", state="disabled")
            for sv in services:
                label_text = f"{sv[3]} - {sv[4]:,}đ"
                sub_menu.add_command(label=label_text, command=lambda item=sv: add_service_to_list(item))
            service_menu.add_cascade(label=c[1], menu=sub_menu)
            
        def post_menu():
            x = menu_btn.winfo_rootx()
            y = menu_btn.winfo_rooty() + menu_btn.winfo_height()
            service_menu.post(x, y)
            
        menu_btn.configure(command=post_menu)
        
        # Nature: RadioButtonGroup
        tk.Label(form_frame, text="Tính chất sửa chữa *:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        nature_var = tk.StringVar(value=slip["nature"])
        nat_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        nat_frame.pack(fill="x", pady=(0, 10))
        
        date_picker_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        
        tk.Label(date_picker_frame, text="Từ ngày:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        start_date_picker = DateEntry(date_picker_frame, width=15, background=ui_helpers.COLOR_PRIMARY_DARK, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        start_date_picker.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(date_picker_frame, text="Đến ngày:", bg=ui_helpers.COLOR_WHITE, fg="#666666", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w", padx=15)
        end_date_picker = DateEntry(date_picker_frame, width=15, background=ui_helpers.COLOR_PRIMARY_DARK, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        end_date_picker.grid(row=0, column=3, padx=5, pady=5)
        
        # Populate dates if Hen
        if slip["nature"] == "Hen":
            start_date_picker.set_date(datetime.strptime(slip["start_date"], "%Y-%m-%d"))
            end_date_picker.set_date(datetime.strptime(slip["end_date"], "%Y-%m-%d"))
            
        def on_nature_change():
            val = nature_var.get()
            if val == "Hen":
                date_picker_frame.pack(fill="x", pady=5, after=nat_frame)
            else:
                date_picker_frame.pack_forget()
                
        r1 = tk.Radiobutton(nat_frame, text="Lấy liền", bg=ui_helpers.COLOR_WHITE, variable=nature_var, value="LayLien", command=on_nature_change)
        r1.pack(side="left", padx=10)
        
        r2 = tk.Radiobutton(nat_frame, text="Hẹn lịch", bg=ui_helpers.COLOR_WHITE, variable=nature_var, value="Hen", command=on_nature_change)
        r2.pack(side="left", padx=10)
        
        on_nature_change()
        render_selected_services()
        
        # Bottom Actions
        btn_frame = tk.Frame(form_frame, bg=ui_helpers.COLOR_WHITE)
        btn_frame.pack(side="bottom", fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(
            btn_frame, text="Hủy bỏ", bg=ui_helpers.COLOR_BG_LIGHT, fg="#666666",
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=15, pady=6, cursor="hand2",
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        def save():
            title = slip_name_entry.get().strip()
            cust_val = cust_combo.get()
            nature = nature_var.get()
            
            if not title or not cust_val or not selected_services:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=dialog)
                return
                
            kh_id = int(cust_val.split(" - ")[0])
            
            start_d = None
            end_d = None
            if nature == "Hen":
                start_d = start_date_picker.get()
                end_d = end_date_picker.get()
                
                try:
                    sd = datetime.strptime(start_d, "%Y-%m-%d")
                    ed = datetime.strptime(end_d, "%Y-%m-%d")
                    if sd > ed:
                        messagebox.showerror("Lỗi ngày hẹn", "Ngày hẹn bắt đầu không thể sau ngày kết thúc!", parent=dialog)
                        return
                except:
                    messagebox.showerror("Lỗi", "Định dạng ngày hẹn không hợp lệ!", parent=dialog)
                    return
                    
            sv_tuples = [(s[0], s[2]) for s in selected_services]
            
            try:
                db.update_slip(slip["id"], title, kh_id, self.current_user["id"], nature, start_d, end_d, sv_tuples)
                messagebox.showinfo("Thành công", "Đã cập nhật lịch hẹn/phiếu sửa chữa thành công!", parent=dialog)
                dialog.destroy()
                self.load_manager_customer_care()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật phiếu sửa chữa:\n{e}", parent=dialog)
                
        save_btn = tk.Button(
            btn_frame, text="Lưu thay đổi", bg=ui_helpers.COLOR_PRIMARY_DARK, fg=ui_helpers.COLOR_WHITE,
            bd=0, relief="flat", font=("Arial", 9, "bold"), padx=15, pady=6, cursor="hand2",
            command=save
        )
        save_btn.pack(side="right", padx=5)
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_ACTIVE_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=ui_helpers.COLOR_PRIMARY_DARK))

if __name__ == "__main__":
    app = GarageApp()
    app.mainloop()
