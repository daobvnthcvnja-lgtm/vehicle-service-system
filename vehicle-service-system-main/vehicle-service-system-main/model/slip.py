class RepairSlip:
    def __init__(self, slip_id=None, title="", customer_id=None, customer_name="", customer_address="", customer_phone="",
                 staff_id=None, staff_name="", nature="", start_date=None, end_date=None, created_at=None, services=None):
        self.slip_id = slip_id
        self.title = title
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_address = customer_address
        self.customer_phone = customer_phone
        self.staff_id = staff_id
        self.staff_name = staff_name
        self.nature = nature
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.services = services or [] # List of tuples/rows: (MaDV, TenDichVu, DonGia, TenLoai)
