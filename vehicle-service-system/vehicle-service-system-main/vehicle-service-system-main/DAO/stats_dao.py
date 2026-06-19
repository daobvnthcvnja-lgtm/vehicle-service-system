from datetime import datetime
from db.database import get_connection

class StatsDAO:
    @staticmethod
    def get_stats_today():
        conn = get_connection()
        cursor = conn.cursor()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            "SELECT COUNT(*) FROM PhieuSuaChua WHERE date(NgayTao) = date(?);",
            (today_str,)
        )
        vehicles_today = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT SUM(SoTien) FROM ThanhToan WHERE date(NgayThu) = date(?);",
            (today_str,)
        )
        revenue_today = cursor.fetchone()[0]
        if revenue_today is None:
            revenue_today = 0
            
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

    @staticmethod
    def get_category_distribution_last_quarter():
        conn = get_connection()
        cursor = conn.cursor()
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

    @staticmethod
    def get_monthly_revenue():
        conn = get_connection()
        cursor = conn.cursor()
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

    @staticmethod
    def get_top_staff():
        conn = get_connection()
        cursor = conn.cursor()
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

    @staticmethod
    def get_top_customers():
        conn = get_connection()
        cursor = conn.cursor()
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

# For backward compatibility
get_stats_today = StatsDAO.get_stats_today
get_category_distribution_last_quarter = StatsDAO.get_category_distribution_last_quarter
get_monthly_revenue = StatsDAO.get_monthly_revenue
get_top_staff = StatsDAO.get_top_staff
get_top_customers = StatsDAO.get_top_customers
