import sqlite3
import os

db_path = r"D:\sqtlite\db_sqlite_studio\garage.db"
print("DB Path:", db_path)
print("DB Exists:", os.path.exists(db_path))

try:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check NhanVien table
    if ('NhanVien',) in tables:
        cursor.execute("SELECT * FROM NhanVien;")
        print("NhanVien entries:", cursor.fetchall())
        
    conn.close()
except Exception as e:
    print("Error:", e)
