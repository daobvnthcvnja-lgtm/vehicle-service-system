class Staff:
    def __init__(self, staff_id=None, name="", username="", password="", role="", is_deleted=0):
        self.staff_id = staff_id
        self.name = name
        self.username = username
        self.password = password
        self.role = role
        self.is_deleted = is_deleted

    @staticmethod
    def from_row(row):
        if not row:
            return None
        # Assuming row is (MaNV, HoTen, TenDangNhap, MatKhau, VaiTro)
        return Staff(
            staff_id=row[0],
            name=row[1],
            username=row[2],
            password=row[3],
            role=row[4]
        )
