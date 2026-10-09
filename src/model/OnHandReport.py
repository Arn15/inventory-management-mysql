class OnHandReport:
    def __init__(self, version, product_lot_number, quantity):
        self.version = version
        self.product_lot_number = product_lot_number
        self.quantity = quantity

    def display(self):
        print(f"Version: {self.version}, Product Lot Number: {self.product_lot_number}, "
              f"Remaining Amount: {self.quantity}")
        
    def get_header(self):
        return ['version', 'product_lot_number', 'quantity']
    
    def get_content(self):
        return [self.version, self.product_lot_number, self.quantity]