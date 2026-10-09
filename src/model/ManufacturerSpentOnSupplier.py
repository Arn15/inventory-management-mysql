class ManufacturerSpentOnSupplier:
    def __init__(self, supplier_id, supplier_name, total_spent):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.total_spent = total_spent

    def display(self):
        print(f"Supplier Name: {self.supplier_name}, Total Spent: {self.total_spent}")

    def get_header(self):
        return ['Supplier Name', 'Total Spent']
    
    def get_content(self):
        return [self.supplier_name, self.total_spent]