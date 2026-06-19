class Customer:
    def __init__(self, customer_id=None, name="", phone="", address="", is_deleted=0):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.address = address
        self.is_deleted = is_deleted

    @staticmethod
    def from_row(row):
        if not row:
            return None
        # Assuming row is (MaKH, HoTen, SoDienThoai, DiaChi)
        return Customer(
            customer_id=row[0],
            name=row[1],
            phone=row[2],
            address=row[3]
        )
