from db.database import get_connection
from DAO.staff_dao import StaffDAO

class SlipDAO:
    @staticmethod
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

    @staticmethod
    def create_slip(title, kh_id, nv_id, nature, start_date, end_date, selected_services):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO PhieuSuaChua (TenPhieu, MaKH, MaNV, TinhChat, NgayHenBatDau, NgayHenKetThuc)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (title, kh_id, nv_id, nature, start_date, end_date)
            )
            slip_id = cursor.lastrowid
            
            total_amount = 0
            for sv_id, price in selected_services:
                cursor.execute(
                    "INSERT INTO ChiTietPhieu (MaPhieu, MaDV, DonGia) VALUES (?, ?, ?);",
                    (slip_id, sv_id, price)
                )
                total_amount += price
                
            cursor.execute(
                "INSERT INTO HoaDon (MaPhieu, TongTien, TrangThai) VALUES (?, ?, 'ChuaThanhToan');",
                (slip_id, total_amount)
            )
            
            conn.commit()
            StaffDAO.log_action(nv_id, f"Tạo phiếu sửa chữa mới ID: {slip_id} (Hóa đơn tương ứng được khởi tạo: {total_amount}đ)")
            return slip_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_slip(slip_id, title, kh_id, nv_id, nature, start_date, end_date, selected_services):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE PhieuSuaChua 
                SET TenPhieu = ?, MaKH = ?, TinhChat = ?, NgayHenBatDau = ?, NgayHenKetThuc = ?
                WHERE MaPhieu = ?;
                """,
                (title, kh_id, nature, start_date, end_date, slip_id)
            )
            
            cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
            
            total_amount = 0
            for sv_id, price in selected_services:
                cursor.execute(
                    "INSERT INTO ChiTietPhieu (MaPhieu, MaDV, DonGia) VALUES (?, ?, ?);",
                    (slip_id, sv_id, price)
                )
                total_amount += price
                
            cursor.execute(
                "UPDATE HoaDon SET TongTien = ? WHERE MaPhieu = ?;",
                (total_amount, slip_id)
            )
            
            conn.commit()
            StaffDAO.log_action(nv_id, f"Cập nhật phiếu sửa chữa ID: {slip_id} (Hóa đơn cập nhật tổng tiền: {total_amount}đ)")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_slip(slip_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM ThanhToan WHERE MaHD IN (SELECT MaHD FROM HoaDon WHERE MaPhieu = ?);",
                (slip_id,)
            )
            cursor.execute("DELETE FROM HoaDon WHERE MaPhieu = ?;", (slip_id,))
            cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
            cursor.execute("DELETE FROM PhieuSuaChua WHERE MaPhieu = ?;", (slip_id,))
            conn.commit()
            if nv_id:
                StaffDAO.log_action(nv_id, f"Xóa phiếu sửa chữa ID: {slip_id} và các hóa đơn/chi tiết liên quan")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# For backward compatibility
get_slips = SlipDAO.get_slips
create_slip = SlipDAO.create_slip
update_slip = SlipDAO.update_slip
delete_slip = SlipDAO.delete_slip
