class Invoice:
    def __init__(self, invoice_id=None, slip_id=None, slip_name="", customer_name="", customer_address="",
                 total_amount=0, status="", payment_date=None, payment_method="N/A", services=None):
        self.invoice_id = invoice_id
        self.slip_id = slip_id
        self.slip_name = slip_name
        self.customer_name = customer_name
        self.customer_address = customer_address
        self.total_amount = total_amount
        self.status = status
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.services = services or [] # List of tuples/rows: (TenDichVu, DonGia, TenLoai)
