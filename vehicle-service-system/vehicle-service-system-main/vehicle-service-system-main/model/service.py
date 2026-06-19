class Category:
    def __init__(self, category_id=None, name="", is_deleted=0):
        self.category_id = category_id
        self.name = name
        self.is_deleted = is_deleted

    @staticmethod
    def from_row(row):
        if not row:
            return None
        # Assuming row is (MaLoai, TenLoai)
        return Category(
            category_id=row[0],
            name=row[1]
        )


class Service:
    def __init__(self, service_id=None, category_id=None, category_name="", name="", price=0, is_deleted=0):
        self.service_id = service_id
        self.category_id = category_id
        self.category_name = category_name
        self.name = name
        self.price = price
        self.is_deleted = is_deleted

    @staticmethod
    def from_row(row):
        if not row:
            return None
        # Assuming row is (MaDV, MaLoai, TenLoai, TenDichVu, Gia)
        return Service(
            service_id=row[0],
            category_id=row[1],
            category_name=row[2],
            name=row[3],
            price=row[4]
        )
