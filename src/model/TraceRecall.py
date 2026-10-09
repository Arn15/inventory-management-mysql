class TraceRecall:
    def __init__(self, product_lot_number, expiration_date, product_id, product_name, manufacturer_name):
        self.product_lot_number = product_lot_number
        self.expiration_date = expiration_date
        self.product_id = product_id
        self.product_name = product_name
        self.manufacturer_name = manufacturer_name

    def display(self):
        print(f"Product Lot Number: {self.product_lot_number}, Product Name: {self.product_name}, "
              f"Manufacturer Name: {self.manufacturer_name}, Expiration Date: {self.expiration_date}")
    
    def get_header(self):
        return ['Product Lot Number', 'Expiration Date', 'Product Name', 'Manufacturer Name']
    
    def get_content(self):
        return [self.product_lot_number, self.product_name, self.manufacturer_name, self.expiration_date]