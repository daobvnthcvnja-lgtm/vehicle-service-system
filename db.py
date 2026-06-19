import sqlite3
import os
from datetime import datetime

DB_PATH = r"D:\sqtlite\db_sqlite_studio\garage.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    # Tables are already created as verified, but we can write a fallback check
    conn = get_connection()
    cursor = conn.cursor()
    # Check if NhanVien table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='NhanVien';")
    if not cursor.fetchone():
        # Fallback table initialization if database is empty
        sql_script = """
        CREATE TABLE IF NOT EXISTS NhanVien (
            MaNV INTEGER PRIMARY KEY AUTOINCREMENT,
            HoTen TEXT NOT NULL,
            TenDangNhap TEXT UNIQUE NOT NULL,
            MatKhau TEXT NOT NULL,
            VaiTro TEXT NOT NULL CHECK(VaiTro IN ('QuanLy','NhanVien')),
            DaXoa INTEGER DEFAULT 0
        );
        INSERT OR IGNORE INTO NhanVien (HoTen,TenDangNhap,MatKhau,VaiTro) VALUES ('Administrator','a','123','QuanLy');
        CREATE TABLE IF NOT EXISTS KhachHang (
            MaKH INTEGER PRIMARY KEY AUTOINCREMENT,
            HoTen TEXT NOT NULL,
            SoDienThoai TEXT,
            DiaChi TEXT,
            DaXoa INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS PhanLoaiDichVu (
            MaLoai INTEGER PRIMARY KEY AUTOINCREMENT,
            TenLoai TEXT NOT NULL,
            DaXoa INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS DichVu (
            MaDV INTEGER PRIMARY KEY AUTOINCREMENT,
            MaLoai INTEGER NOT NULL,
            TenDichVu TEXT NOT NULL,
            Gia INTEGER NOT NULL DEFAULT 0,
            DaXoa INTEGER DEFAULT 0,
            FOREIGN KEY(MaLoai) REFERENCES PhanLoaiDichVu(MaLoai)
        );
        CREATE TABLE IF NOT EXISTS PhieuSuaChua (
            MaPhieu INTEGER PRIMARY KEY AUTOINCREMENT,
            TenPhieu TEXT NOT NULL,
            MaKH INTEGER NOT NULL,
            MaNV INTEGER NOT NULL,
            TinhChat TEXT NOT NULL CHECK(TinhChat IN ('LayLien','Hen')),
            NgayHenBatDau DATE,
            NgayHenKetThuc DATE,
            NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHECK (TinhChat = 'LayLien' OR (NgayHenBatDau IS NOT NULL AND NgayHenKetThuc IS NOT NULL)),
            FOREIGN KEY(MaKH) REFERENCES KhachHang(MaKH),
            FOREIGN KEY(MaNV) REFERENCES NhanVien(MaNV)
        );
        CREATE TABLE IF NOT EXISTS ChiTietPhieu (
            MaCT INTEGER PRIMARY KEY AUTOINCREMENT,
            MaPhieu INTEGER NOT NULL,
            MaDV INTEGER NOT NULL,
            DonGia INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(MaPhieu) REFERENCES PhieuSuaChua(MaPhieu),
            FOREIGN KEY(MaDV) REFERENCES DichVu(MaDV)
        );
        CREATE TABLE IF NOT EXISTS HoaDon (
            MaHD INTEGER PRIMARY KEY AUTOINCREMENT,
            MaPhieu INTEGER UNIQUE NOT NULL,
            TongTien INTEGER DEFAULT 0,
            TrangThai TEXT DEFAULT 'ChuaThanhToan' CHECK(TrangThai IN ('ChuaThanhToan','DaThanhToan')),
            NgayThanhToan DATETIME,
            FOREIGN KEY(MaPhieu) REFERENCES PhieuSuaChua(MaPhieu)
        );
        CREATE TABLE IF NOT EXISTS ThanhToan (
            MaTT INTEGER PRIMARY KEY AUTOINCREMENT,
            MaHD INTEGER NOT NULL,
            PhuongThuc TEXT CHECK(PhuongThuc IN ('TienMat','ChuyenKhoan')),
            SoTien INTEGER,
            NgayThu DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(MaHD) REFERENCES HoaDon(MaHD)
        );
        CREATE TABLE IF NOT EXISTS NhatKyHoatDong (
            MaLog INTEGER PRIMARY KEY AUTOINCREMENT,
            MaNV INTEGER,
            HanhDong TEXT,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(MaNV) REFERENCES NhanVien(MaNV)
        );
        CREATE TABLE IF NOT EXISTS LichSuGia (
            MaLS INTEGER PRIMARY KEY AUTOINCREMENT,
            MaDV INTEGER NOT NULL,
            GiaCu INTEGER NOT NULL,
            GiaMoi INTEGER NOT NULL,
            NgayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP,
            MaNV INTEGER,
            FOREIGN KEY(MaDV) REFERENCES DichVu(MaDV),
            FOREIGN KEY(MaNV) REFERENCES NhanVien(MaNV)
        );
        """
        cursor.executescript(sql_script)
        conn.commit()
    conn.close()

# Log operations
def log_action(nv_id, action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO NhatKyHoatDong (MaNV, HanhDong) VALUES (?, ?);",
        (nv_id, action)
    )
    conn.commit()
    conn.close()

# Authentication
def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT MaNV, HoTen, TenDangNhap, VaiTro FROM NhanVien WHERE TenDangNhap = ? AND MatKhau = ? AND DaXoa = 0;",
        (username, password)
    )
    res = cursor.fetchone()
    conn.close()
    if res:
        log_action(res[0], f"Đăng nhập hệ thống (Vai trò: {res[3]})")
        return {"id": res[0], "name": res[1], "username": res[2], "role": res[3]}
    return None

# Customers CRUD
def get_customers(search_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        # Search all fields
        like_query = f"%{search_query}%"
        cursor.execute(
            "SELECT MaKH, HoTen, SoDienThoai, DiaChi FROM KhachHang WHERE DaXoa = 0 AND (MaKH LIKE ? OR HoTen LIKE ? OR SoDienThoai LIKE ? OR DiaChi LIKE ?);",
            (like_query, like_query, like_query, like_query)
        )
    else:
        cursor.execute("SELECT MaKH, HoTen, SoDienThoai, DiaChi FROM KhachHang WHERE DaXoa = 0;")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_customer(name, phone, address, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO KhachHang (HoTen, SoDienThoai, DiaChi) VALUES (?, ?, ?);",
        (name, phone, address)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Thêm khách hàng mới ID: {new_id} - Tên: {name}")
    return new_id

def update_customer(kh_id, name, phone, address, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE KhachHang SET HoTen = ?, SoDienThoai = ?, DiaChi = ? WHERE MaKH = ?;",
        (name, phone, address, kh_id)
    )
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Cập nhật thông tin khách hàng ID: {kh_id}")

def delete_customer(kh_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    # Soft delete
    cursor.execute("UPDATE KhachHang SET DaXoa = 1 WHERE MaKH = ?;", (kh_id,))
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Xóa khách hàng ID: {kh_id}")

# Service categories
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaLoai, TenLoai FROM PhanLoaiDichVu WHERE DaXoa = 0;")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_category(name, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PhanLoaiDichVu (TenLoai) VALUES (?);", (name,))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Thêm phân loại dịch vụ: {name} (ID: {new_id})")
    return new_id

def delete_category(cat_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE PhanLoaiDichVu SET DaXoa = 1 WHERE MaLoai = ?;", (cat_id,))
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Xóa phân loại dịch vụ ID: {cat_id}")

# Services CRUD
def get_services(category_id=None, search_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.MaDV, d.MaLoai, p.TenLoai, d.TenDichVu, d.Gia 
        FROM DichVu d
        JOIN PhanLoaiDichVu p ON d.MaLoai = p.MaLoai
        WHERE d.DaXoa = 0 AND p.DaXoa = 0
    """
    params = []
    if category_id:
        query += " AND d.MaLoai = ?"
        params.append(category_id)
    if search_query:
        query += " AND (d.MaDV LIKE ? OR d.TenDichVu LIKE ? OR p.TenLoai LIKE ? OR d.Gia LIKE ?)"
        like_q = f"%{search_query}%"
        params.extend([like_q] * 4)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_service(category_id, name, price, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO DichVu (MaLoai, TenDichVu, Gia) VALUES (?, ?, ?);",
        (category_id, name, price)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Thêm dịch vụ mới ID: {new_id} - {name} - Giá: {price}")
    return new_id

def update_service(service_id, category_id, name, price, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    # First get old price to record history
    cursor.execute("SELECT Gia, TenDichVu FROM DichVu WHERE MaDV = ?;", (service_id,))
    old_data = cursor.fetchone()
    old_price = old_data[0] if old_data else 0
    old_name = old_data[1] if old_data else ""

    cursor.execute(
        "UPDATE DichVu SET MaLoai = ?, TenDichVu = ?, Gia = ? WHERE MaDV = ?;",
        (category_id, name, price, service_id)
    )
    
    # Record history if price changed
    if old_price != price:
        cursor.execute(
            "INSERT INTO LichSuGia (MaDV, GiaCu, GiaMoi, MaNV) VALUES (?, ?, ?, ?);",
            (service_id, old_price, price, nv_id)
        )
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Cập nhật dịch vụ ID: {service_id} (Tên: {name}, Giá: {price})")

def delete_service(service_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE DichVu SET DaXoa = 1 WHERE MaDV = ?;", (service_id,))
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Xóa dịch vụ ID: {service_id}")

# Staff (NhanVien) CRUD
def get_staff(search_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        like_q = f"%{search_query}%"
        cursor.execute(
            "SELECT MaNV, HoTen, TenDangNhap, MatKhau, VaiTro FROM NhanVien WHERE DaXoa = 0 AND (MaNV LIKE ? OR HoTen LIKE ? OR TenDangNhap LIKE ? OR VaiTro LIKE ?);",
            (like_q, like_q, like_q, like_q)
        )
    else:
        cursor.execute("SELECT MaNV, HoTen, TenDangNhap, MatKhau, VaiTro FROM NhanVien WHERE DaXoa = 0;")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_staff(name, username, password, role, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO NhanVien (HoTen, TenDangNhap, MatKhau, VaiTro) VALUES (?, ?, ?, ?);",
        (name, username, password, role)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Tạo nhân viên mới ID: {new_id} - Tên: {name} - Vai trò: {role}")
    return new_id

def update_staff(staff_id, name, username, password, role, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE NhanVien SET HoTen = ?, TenDangNhap = ?, MatKhau = ?, VaiTro = ? WHERE MaNV = ?;",
        (name, username, password, role, staff_id)
    )
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Cập nhật tài khoản nhân viên ID: {staff_id}")

def delete_staff(staff_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE NhanVien SET DaXoa = 1 WHERE MaNV = ?;", (staff_id,))
    conn.commit()
    conn.close()
    if nv_id:
        log_action(nv_id, f"Xóa tài khoản nhân viên ID: {staff_id}")

# Repair Slips CRUD
def get_slips(search_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.MaPhieu, p.TenPhieu, p.MaKH, k.HoTen, k.DiaChi, k.SoDienThoai, p.MaNV, n.HoTen, 
               p.TinhChat, p.NgayHenBatDau, p.NgayHenKetThuc, p.NgayTao
        FROM PhieuSuaChua p
        JOIN KhachHang k ON p.MaKH = k.MaKH
        JOIN NhanVien n ON p.MaNV = n.MaNV
    """
    params = []
    if search_query:
        query += """ WHERE p.MaPhieu LIKE ? OR p.TenPhieu LIKE ? OR k.HoTen LIKE ? OR k.SoDienThoai LIKE ? 
                     OR p.TinhChat LIKE ? OR p.NgayHenBatDau LIKE ? OR p.NgayHenKetThuc LIKE ? OR p.NgayTao LIKE ?"""
        like_q = f"%{search_query}%"
        params.extend([like_q] * 8)
    query += " ORDER BY p.MaPhieu ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Load details for each slip
    result = []
    for row in rows:
        slip_id = row[0]
        cursor.execute(
            """
            SELECT c.MaDV, d.TenDichVu, c.DonGia, l.TenLoai
            FROM ChiTietPhieu c
            JOIN DichVu d ON c.MaDV = d.MaDV
            JOIN PhanLoaiDichVu l ON d.MaLoai = l.MaLoai
            WHERE c.MaPhieu = ?;
            """,
            (slip_id,)
        )
        services = cursor.fetchall()
        result.append({
            "id": row[0],
            "title": row[1],
            "customer_id": row[2],
            "customer_name": row[3],
            "customer_address": row[4],
            "customer_phone": row[5],
            "staff_id": row[6],
            "staff_name": row[7],
            "nature": row[8],
            "start_date": row[9],
            "end_date": row[10],
            "created_at": row[11],
            "services": services
        })
    conn.close()
    return result

def create_slip(title, kh_id, nv_id, nature, start_date, end_date, selected_services):
    # selected_services: list of dict or tuple (MaDV, Gia)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insert into PhieuSuaChua
        cursor.execute(
            """
            INSERT INTO PhieuSuaChua (TenPhieu, MaKH, MaNV, TinhChat, NgayHenBatDau, NgayHenKetThuc)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (title, kh_id, nv_id, nature, start_date, end_date)
        )
        slip_id = cursor.lastrowid
        
        # Insert details
        total_amount = 0
        for sv_id, price in selected_services:
            cursor.execute(
                "INSERT INTO ChiTietPhieu (MaPhieu, MaDV, DonGia) VALUES (?, ?, ?);",
                (slip_id, sv_id, price)
            )
            total_amount += price
            
        # Automatically create Invoice in HoaDon table
        cursor.execute(
            "INSERT INTO HoaDon (MaPhieu, TongTien, TrangThai) VALUES (?, ?, 'ChuaThanhToan');",
            (slip_id, total_amount)
        )
        
        conn.commit()
        log_action(nv_id, f"Tạo phiếu sửa chữa mới ID: {slip_id} (Hóa đơn tương ứng được khởi tạo: {total_amount}đ)")
        return slip_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_slip(slip_id, title, kh_id, nv_id, nature, start_date, end_date, selected_services):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Update PhieuSuaChua
        cursor.execute(
            """
            UPDATE PhieuSuaChua 
            SET TenPhieu = ?, MaKH = ?, TinhChat = ?, NgayHenBatDau = ?, NgayHenKetThuc = ?
            WHERE MaPhieu = ?;
            """,
            (title, kh_id, nature, start_date, end_date, slip_id)
        )
        
        # Delete old details
        cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
        
        # Insert new details
        total_amount = 0
        for sv_id, price in selected_services:
            cursor.execute(
                "INSERT INTO ChiTietPhieu (MaPhieu, MaDV, DonGia) VALUES (?, ?, ?);",
                (slip_id, sv_id, price)
            )
            total_amount += price
            
        # Update corresponding invoice total price
        cursor.execute(
            "UPDATE HoaDon SET TongTien = ? WHERE MaPhieu = ?;",
            (total_amount, slip_id)
        )
        
        conn.commit()
        log_action(nv_id, f"Cập nhật phiếu sửa chữa ID: {slip_id} (Hóa đơn cập nhật tổng tiền: {total_amount}đ)")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_slip(slip_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Need to clean up details, invoice, payment first to prevent foreign key errors, or because PRAGMA foreign_keys is ON
        # Actually since we want to delete, we delete in correct order:
        # 1. ThanhToan where MaHD in (select MaHD from HoaDon where MaPhieu = slip_id)
        # 2. HoaDon where MaPhieu = slip_id
        # 3. ChiTietPhieu where MaPhieu = slip_id
        # 4. PhieuSuaChua where MaPhieu = slip_id
        cursor.execute(
            "DELETE FROM ThanhToan WHERE MaHD IN (SELECT MaHD FROM HoaDon WHERE MaPhieu = ?);",
            (slip_id,)
        )
        cursor.execute("DELETE FROM HoaDon WHERE MaPhieu = ?;", (slip_id,))
        cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
        cursor.execute("DELETE FROM PhieuSuaChua WHERE MaPhieu = ?;", (slip_id,))
        conn.commit()
        if nv_id:
            log_action(nv_id, f"Xóa phiếu sửa chữa ID: {slip_id} và các hóa đơn/chi tiết liên quan")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Invoices and Payments
def get_invoices(search_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT h.MaHD, h.MaPhieu, p.TenPhieu, k.HoTen, k.DiaChi, h.TongTien, h.TrangThai, h.NgayThanhToan, t.PhuongThuc
        FROM HoaDon h
        JOIN PhieuSuaChua p ON h.MaPhieu = p.MaPhieu
        JOIN KhachHang k ON p.MaKH = k.MaKH
        LEFT JOIN ThanhToan t ON h.MaHD = t.MaHD
    """
    params = []
    if search_query:
        query += """ WHERE h.MaHD LIKE ? OR h.MaPhieu LIKE ? OR p.TenPhieu LIKE ? OR k.HoTen LIKE ? 
                     OR h.TongTien LIKE ? OR h.TrangThai LIKE ? OR h.NgayThanhToan LIKE ?"""
        like_q = f"%{search_query}%"
        params.extend([like_q] * 7)
    query += " ORDER BY h.MaHD ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Load services for invoice details
    result = []
    for r in rows:
        hd_id = r[0]
        slip_id = r[1]
        cursor.execute(
            """
            SELECT d.TenDichVu, c.DonGia, l.TenLoai
            FROM ChiTietPhieu c
            JOIN DichVu d ON c.MaDV = d.MaDV
            JOIN PhanLoaiDichVu l ON d.MaLoai = l.MaLoai
            WHERE c.MaPhieu = ?;
            """,
            (slip_id,)
        )
        services = cursor.fetchall()
        
        result.append({
            "id": r[0],
            "slip_id": r[1],
            "slip_name": r[2],
            "customer_name": r[3],
            "customer_address": r[4],
            "total_amount": r[5],
            "status": r[6],
            "payment_date": r[7],
            "payment_method": r[8] if r[8] else "N/A",
            "services": services
        })
    conn.close()
    return result

def pay_invoice(hd_id, method, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get total amount
        cursor.execute("SELECT TongTien, TrangThai FROM HoaDon WHERE MaHD = ?;", (hd_id,))
        invoice = cursor.fetchone()
        if not invoice:
            raise Exception("Hóa đơn không tồn tại.")
        total_amount = invoice[0]
        
        # Check if already paid
        if invoice[1] == 'DaThanhToan':
            raise Exception("Hóa đơn đã được thanh toán trước đó.")
            
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update HoaDon status
        cursor.execute(
            "UPDATE HoaDon SET TrangThai = 'DaThanhToan', NgayThanhToan = ? WHERE MaHD = ?;",
            (now_str, hd_id)
        )
        
        # Insert into ThanhToan
        cursor.execute(
            "INSERT INTO ThanhToan (MaHD, PhuongThuc, SoTien, NgayThu) VALUES (?, ?, ?, ?);",
            (hd_id, method, total_amount, now_str)
        )
        
        conn.commit()
        if nv_id:
            log_action(nv_id, f"Thu tiền hóa đơn ID: {hd_id} - Phương thức: {method} - Số tiền: {total_amount}đ")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_invoice(hd_id, nv_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Find MaPhieu for this HoaDon
        cursor.execute("SELECT MaPhieu FROM HoaDon WHERE MaHD = ?;", (hd_id,))
        row = cursor.fetchone()
        if row:
            slip_id = row[0]
            # Delete in cascade order:
            cursor.execute("DELETE FROM ThanhToan WHERE MaHD = ?;", (hd_id,))
            cursor.execute("DELETE FROM HoaDon WHERE MaHD = ?;", (hd_id,))
            cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
            cursor.execute("DELETE FROM PhieuSuaChua WHERE MaPhieu = ?;", (slip_id,))
        conn.commit()
        if nv_id:
            log_action(nv_id, f"Xóa hóa đơn ID: {hd_id} và các phiếu sửa chữa liên quan")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Dashboard Stats queries
def get_stats_today():
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Số xe sửa ngày hôm nay: tickets created today
    cursor.execute(
        "SELECT COUNT(*) FROM PhieuSuaChua WHERE date(NgayTao) = date(?);",
        (today_str,)
    )
    vehicles_today = cursor.fetchone()[0]
    
    # 2. Doanh thu hôm nay: total of payments collected today
    cursor.execute(
        "SELECT SUM(SoTien) FROM ThanhToan WHERE date(NgayThu) = date(?);",
        (today_str,)
    )
    revenue_today = cursor.fetchone()[0]
    if revenue_today is None:
        revenue_today = 0
        
    # 3. Dịch vụ phổ biến hôm nay
    cursor.execute(
        """
        SELECT d.TenDichVu, COUNT(*) as cnt
        FROM ChiTietPhieu c
        JOIN PhieuSuaChua p ON c.MaPhieu = p.MaPhieu
        JOIN DichVu d ON c.MaDV = d.MaDV
        WHERE date(p.NgayTao) = date(?)
        GROUP BY c.MaDV
        ORDER BY cnt DESC
        LIMIT 1;
        """,
        (today_str,)
    )
    pop_service = cursor.fetchone()
    popular_today = pop_service[0] if pop_service else "Không có"
    
    conn.close()
    return {
        "vehicles": vehicles_today,
        "revenue": revenue_today,
        "popular_service": popular_today
    }

def get_category_distribution_last_quarter():
    conn = get_connection()
    cursor = conn.cursor()
    # 3 months ago query (using sqlite datetime modifiers)
    cursor.execute(
        """
        SELECT l.TenLoai, COUNT(c.MaDV) as cnt
        FROM ChiTietPhieu c
        JOIN PhieuSuaChua p ON c.MaPhieu = p.MaPhieu
        JOIN DichVu d ON c.MaDV = d.MaDV
        JOIN PhanLoaiDichVu l ON d.MaLoai = l.MaLoai
        WHERE p.NgayTao >= datetime('now', '-3 months')
        GROUP BY l.MaLoai;
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_monthly_revenue():
    conn = get_connection()
    cursor = conn.cursor()
    # Monthly revenue for past 6 months
    cursor.execute(
        """
        SELECT strftime('%m/%Y', NgayThu) as mth, SUM(SoTien)
        FROM ThanhToan
        WHERE NgayThu >= datetime('now', '-6 months')
        GROUP BY mth
        ORDER BY NgayThu ASC;
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_top_staff():
    conn = get_connection()
    cursor = conn.cursor()
    # Rank by number of actions in NhatKyHoatDong for employees only
    cursor.execute(
        """
        SELECT n.HoTen, COUNT(l.MaLog) as cnt
        FROM NhatKyHoatDong l
        JOIN NhanVien n ON l.MaNV = n.MaNV
        WHERE n.DaXoa = 0 AND n.VaiTro = 'NhanVien'
        GROUP BY l.MaNV
        ORDER BY cnt DESC
        LIMIT 5;
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_top_customers():
    conn = get_connection()
    cursor = conn.cursor()
    # Rank by number of slips
    cursor.execute(
        """
        SELECT k.HoTen, COUNT(p.MaPhieu) as cnt
        FROM PhieuSuaChua p
        JOIN KhachHang k ON p.MaKH = k.MaKH
        WHERE k.DaXoa = 0
        GROUP BY p.MaKH
        ORDER BY cnt DESC
        LIMIT 5;
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
