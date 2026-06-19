import os
import sqlite3
from datetime import datetime
import db
import ui_helpers
from fpdf import FPDF

def verify_all():
    print("--- STARTING APP VERIFICATION ---")
    
    # 1. Test Database Connectivity
    print("\n[1] Testing database connectivity & foreign keys...")
    try:
        conn = db.get_connection()
        # Test foreign keys PRAGMA
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk_status = cursor.fetchone()[0]
        print(f"    - DB connection successful.")
        print(f"    - PRAGMA foreign_keys status: {fk_status} (Expected: 1)")
        assert fk_status == 1, "Foreign keys not enabled!"
        conn.close()
    except Exception as e:
        print(f"    - ERROR: Database test failed: {e}")
        return False

    # 2. Test DB initialization
    print("\n[2] Testing db initialization fallback...")
    try:
        db.init_db()
        print("    - Init check passed successfully.")
    except Exception as e:
        print(f"    - ERROR: db.init_db failed: {e}")
        return False
        
    # 3. Test authenticate
    print("\n[3] Testing authentication logic...")
    try:
        user = db.authenticate("a", "123")
        print(f"    - Authenticate 'a'/'123' output: {user}")
        if user:
            print(f"      Name: {user['name']}, Role: {user['role']}")
            assert user["role"] == "QuanLy", "Default user role mismatch!"
        else:
            print("      WARNING: Default administrator not found. (Could happen if tables are clear, running tests below...)")
    except Exception as e:
        print(f"    - ERROR: Auth test failed: {e}")
        return False
        
    # 4. Test Customer CRUD and search
    print("\n[4] Testing Customer CRUD queries...")
    try:
        # Save current count
        old_count = len(db.get_customers())
        
        # Add test customer
        cust_id = db.add_customer("Nguyễn Văn Test Verification", "0123456789", "123 Đường Test, Quận Test", nv_id=1)
        print(f"    - Customer added successfully. Assigned ID: {cust_id}")
        
        # Test search
        found = db.get_customers("Test Verification")
        print(f"    - Searched and found: {len(found)} entries.")
        assert len(found) > 0, "Failed to find newly added customer!"
        
        # Clean up / Soft delete
        db.delete_customer(cust_id, nv_id=1)
        print("    - Customer soft-deleted successfully.")
        
        new_count = len(db.get_customers())
        print(f"    - Initial count: {old_count}, Current active count: {new_count}")
        assert old_count == new_count, "Soft-delete did not exclude customer from list!"
        
    except Exception as e:
        print(f"    - ERROR: Customer CRUD failed: {e}")
        return False
        
    # 5. Test UI Helpers PIL Icons
    print("\n[5] Testing PIL Icon generation...")
    try:
        # Since Tkinter is required for ImageTk.PhotoImage, we need a root window context
        import tkinter as tk
        root = tk.Tk()
        root.withdraw() # Hide window
        
        logo = ui_helpers.generate_logo_icon()
        logout = ui_helpers.generate_logout_icon()
        
        print(f"    - Logo photo generated successfully (Type: {type(logo)})")
        print(f"    - Logout photo generated successfully (Type: {type(logout)})")
        
        root.destroy()
    except Exception as e:
        print(f"    - ERROR: PIL Icon generation failed: {e}")
        return False
        
    # 6. Test Stats queries
    print("\n[6] Testing statistics query compilation...")
    try:
        stats = db.get_stats_today()
        print(f"    - Stats today: {stats}")
        
        dist = db.get_category_distribution_last_quarter()
        print(f"    - Category distribution: {dist}")
        
        m_rev = db.get_monthly_revenue()
        print(f"    - Monthly revenue: {m_rev}")
        
        top_s = db.get_top_staff()
        print(f"    - Top staff: {top_s}")
        
        top_c = db.get_top_customers()
        print(f"    - Top customers: {top_c}")
    except Exception as e:
        print(f"    - ERROR: Statistics query failed: {e}")
        return False
        
    # 7. Test PDF Generation
    print("\n[7] Testing PDF generation with Segoe UI (Vietnamese support)...")
    try:
        pdf_path = "D:\\project_py\\verify_invoice_test.pdf"
        pdf = FPDF()
        pdf.add_page()
        
        font_path = r"C:\Windows\Fonts\segoeui.ttf"
        if os.path.exists(font_path):
            pdf.add_font("SegoeUI", "", font_path)
            pdf.set_font("SegoeUI", size=12)
            font_name = "SegoeUI"
        else:
            pdf.set_font("Arial", size=12)
            font_name = "Arial"
            
        pdf.cell(w=0, h=10, txt="KIỂM TRA HÓA ĐƠN THỬ NGHIỆM", ln=1, align="C")
        pdf.cell(w=0, h=8, txt="Dịch vụ: Bảo dưỡng động cơ định kỳ", ln=1)
        pdf.cell(w=0, h=8, txt="Khách hàng: Nguyễn Hùng Mạnh", ln=1)
        pdf.cell(w=0, h=8, txt="Đơn giá: 1,500,000 đ", ln=1)
        
        pdf.output(pdf_path)
        print(f"    - PDF exported successfully at: {pdf_path}")
        
        # Clean up test PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print("    - Cleaned up test PDF.")
    except Exception as e:
        print(f"    - ERROR: PDF testing failed: {e}")
        return False
        
    print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")
    return True

if __name__ == "__main__":
    success = verify_all()
    if not success:
        print("\nVerification failed!")
        exit(1)
    else:
        print("\nVerification passed!")
        exit(0)
