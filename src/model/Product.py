class Product:
    def __init__(self, product_id, product_name, category_id):
        self.product_id = product_id
        self.product_name = product_name
        self.category_id = category_id

    def __repr__(self):
        return f"<Product(id={self.product_id}, name={self.product_name}, category={self.category_id})>"
    
    def display(self):
        return f"Product: {self.product_name}"
    