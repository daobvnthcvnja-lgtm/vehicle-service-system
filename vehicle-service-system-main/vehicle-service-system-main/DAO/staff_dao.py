import sqlite3
from db.database import get_connection

class StaffDAO:
    @staticmethod
    def log_action(nv_id, action):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO NhatKyHoatDong (MaNV, HanhDong) VALUES (?, ?);",
            (nv_id, action)
        )
        conn.commit()
        conn.close()

    @staticmethod
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
            StaffDAO.log_action(res[0], f"Đăng nhập hệ thống (Vai trò: {res[3]})")
            return {"id": res[0], "name": res[1], "username": res[2], "role": res[3]}
        return None

    @staticmethod
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

    @staticmethod
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
            StaffDAO.log_action(nv_id, f"Tạo nhân viên mới ID: {new_id} - Tên: {name} - Vai trò: {role}")
        return new_id

    @staticmethod
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
            StaffDAO.log_action(nv_id, f"Cập nhật tài khoản nhân viên ID: {staff_id}")

    @staticmethod
    def delete_staff(staff_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE NhanVien SET DaXoa = 1 WHERE MaNV = ?;", (staff_id,))
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Xóa tài khoản nhân viên ID: {staff_id}")

# For backward compatibility
log_action = StaffDAO.log_action
authenticate = StaffDAO.authenticate
get_staff = StaffDAO.get_staff
add_staff = StaffDAO.add_staff
update_staff = StaffDAO.update_staff
delete_staff = StaffDAO.delete_staff
