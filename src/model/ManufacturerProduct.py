from service import ProductService

class ManufacturerProduct:
    def __init__(self, manufacturer_product_id, manufacturer_id, product_id, product_name, version, standard_size):
        self.manufacturer_product_id = manufacturer_product_id
        self.manufacturer_id = manufacturer_id
        self.product_id = product_id
        self.product_name = product_name
        self.version = version
        self.standard_size = standard_size

    def __repr__(self):
        return (f"<ManufacturerProduct(id={self.manufacturer_product_id}, "
                f"manufacturer_id={self.manufacturer_id}, product_id={self.product_id}, "
                f"version={self.version}, standard_size={self.standard_size})>")
    
    def display(self):
        return (f"Product ID: {self.product_name}, Version: {self.version}")