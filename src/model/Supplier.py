class Supplier:
    def __init__(self, supplier_id: int, supplier_name: str, user_id: int):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.user_id = user_id

    def __repr__(self):
        return f"<Supplier(id={self.supplier_id}, name={self.supplier_name}, user_id={self.user_id})>"
    
    def display(self):
        print(f"Supplier Name: {self.supplier_name}, User ID: {self.user_id}")