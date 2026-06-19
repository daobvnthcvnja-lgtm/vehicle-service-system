from datetime import datetime
from db.database import get_connection
from DAO.staff_dao import StaffDAO

class InvoiceDAO:
    @staticmethod
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

    @staticmethod
    def pay_invoice(hd_id, method, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT TongTien, TrangThai FROM HoaDon WHERE MaHD = ?;", (hd_id,))
            invoice = cursor.fetchone()
            if not invoice:
                raise Exception("Hóa đơn không tồn tại.")
            total_amount = invoice[0]
            
            if invoice[1] == 'DaThanhToan':
                raise Exception("Hóa đơn đã được thanh toán trước đó.")
                
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                "UPDATE HoaDon SET TrangThai = 'DaThanhToan', NgayThanhToan = ? WHERE MaHD = ?;",
                (now_str, hd_id)
            )
            
            cursor.execute(
                "INSERT INTO ThanhToan (MaHD, PhuongThuc, SoTien, NgayThu) VALUES (?, ?, ?, ?);",
                (hd_id, method, total_amount, now_str)
            )
            
            conn.commit()
            if nv_id:
                StaffDAO.log_action(nv_id, f"Thu tiền hóa đơn ID: {hd_id} - Phương thức: {method} - Số tiền: {total_amount}đ")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_invoice(hd_id, nv_id=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MaPhieu FROM HoaDon WHERE MaHD = ?;", (hd_id,))
            row = cursor.fetchone()
            if row:
                slip_id = row[0]
                cursor.execute("DELETE FROM ThanhToan WHERE MaHD = ?;", (hd_id,))
                cursor.execute("DELETE FROM HoaDon WHERE MaHD = ?;", (hd_id,))
                cursor.execute("DELETE FROM ChiTietPhieu WHERE MaPhieu = ?;", (slip_id,))
                cursor.execute("DELETE FROM PhieuSuaChua WHERE MaPhieu = ?;", (slip_id,))
            conn.commit()
            if nv_id:
                StaffDAO.log_action(nv_id, f"Xóa hóa đơn ID: {hd_id} và các phiếu sửa chữa liên quan")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# For backward compatibility
get_invoices = InvoiceDAO.get_invoices
pay_invoice = InvoiceDAO.pay_invoice
delete_invoice = InvoiceDAO.delete_invoice
