from db.database import get_connection
from DAO.staff_dao import StaffDAO

class CustomerDAO:
    @staticmethod
    def get_customers(search_query=""):
        conn = get_connection()
        cursor = conn.cursor()
        if search_query:
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

    @staticmethod
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
            StaffDAO.log_action(nv_id, f"Thêm khách hàng mới ID: {new_id} - Tên: {name}")
        return new_id

    @staticmethod
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
            StaffDAO.log_action(nv_id, f"Cập nhật thông tin khách hàng ID: {kh_id}")

    @staticmethod
    def delete_customer(kh_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE KhachHang SET DaXoa = 1 WHERE MaKH = ?;", (kh_id,))
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Xóa khách hàng ID: {kh_id}")
            
# For backward compatibility
get_customers = CustomerDAO.get_customers
add_customer = CustomerDAO.add_customer
update_customer = CustomerDAO.update_customer
delete_customer = CustomerDAO.delete_customer
