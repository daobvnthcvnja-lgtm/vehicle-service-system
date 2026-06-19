import sqlite3
import os

DB_PATH = r"D:\sqtlite\db_sqlite_studio\garage.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='NhanVien';")
    if not cursor.fetchone():
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
