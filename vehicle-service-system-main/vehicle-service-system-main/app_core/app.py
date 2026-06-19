import tkinter as tk
from tkinter import ttk
import db
from ui.login_view import LoginViewMixin
from ui.main_shell import MainShellMixin
from ui import ui_helpers

class GarageApp(tk.Tk, LoginViewMixin, MainShellMixin):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Trung Tâm Dịch Vụ Và Sửa Chữa Xe")
        self.geometry("800x500")
        self.resizable(False, False)
        
        # Center window
        self.center_window(800, 500)
        
        # Initialize DB tables if not present
        db.init_db()
        
        # Apply global Treeview style (polished tables)
        ui_helpers.configure_treeview_style(ttk.Style(self))
        
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
