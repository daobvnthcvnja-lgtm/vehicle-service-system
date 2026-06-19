from db.database import get_connection
from DAO.staff_dao import StaffDAO

class ServiceDAO:
    @staticmethod
    def get_categories():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaLoai, TenLoai FROM PhanLoaiDichVu WHERE DaXoa = 0;")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_category(name, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO PhanLoaiDichVu (TenLoai) VALUES (?);", (name,))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Thêm phân loại dịch vụ: {name} (ID: {new_id})")
        return new_id

    @staticmethod
    def delete_category(cat_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE PhanLoaiDichVu SET DaXoa = 1 WHERE MaLoai = ?;", (cat_id,))
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Xóa phân loại dịch vụ ID: {cat_id}")

    @staticmethod
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

    @staticmethod
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
            StaffDAO.log_action(nv_id, f"Thêm dịch vụ mới ID: {new_id} - {name} - Gia: {price}")
        return new_id

    @staticmethod
    def update_service(service_id, category_id, name, price, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Gia, TenDichVu FROM DichVu WHERE MaDV = ?;", (service_id,))
        old_data = cursor.fetchone()
        old_price = old_data[0] if old_data else 0

        cursor.execute(
            "UPDATE DichVu SET MaLoai = ?, TenDichVu = ?, Gia = ? WHERE MaDV = ?;",
            (category_id, name, price, service_id)
        )
        
        if old_price != price:
            cursor.execute(
                "INSERT INTO LichSuGia (MaDV, GiaCu, GiaMoi, MaNV) VALUES (?, ?, ?, ?);",
                (service_id, old_price, price, nv_id)
            )
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Cập nhật dịch vụ ID: {service_id} (Tên: {name}, Giá: {price})")

    @staticmethod
    def delete_service(service_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE DichVu SET DaXoa = 1 WHERE MaDV = ?;", (service_id,))
        conn.commit()
        conn.close()
        if nv_id:
            StaffDAO.log_action(nv_id, f"Xóa dịch vụ ID: {service_id}")

# For backward compatibility
get_categories = ServiceDAO.get_categories
add_category = ServiceDAO.add_category
delete_category = ServiceDAO.delete_category
get_services = ServiceDAO.get_services
add_service = ServiceDAO.add_service
update_service = ServiceDAO.update_service
delete_service = ServiceDAO.delete_service
