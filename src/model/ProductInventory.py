
class ProductInventory:
    def __init__(self, product_lot_number, manufacturer_product_id, expiration_date, creation_date, quantity, product_batch_id):
        self.product_lot_number = product_lot_number
        self.manufacturer_product_id = manufacturer_product_id
        self.expiration_date = expiration_date
        self.creation_date = creation_date
        self.quantity = quantity
        self.product_batch_id = product_batch_id

    def display(self):
        print(f"Product Lot Number: {self.product_lot_number}, Creation Date: {self.creation_date}, Expiration Date: {self.expiration_date}, Quantity: {self.quantity}")