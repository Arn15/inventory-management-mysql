class BrowseProductType:
    def __init__(self, category, manufacturer, product, version, standard_size):
        self.category = category
        self.manufacturer = manufacturer
        self.product = product
        self.version = version
        self.standard_size = standard_size

    def display(self):
        print(f"Category: {self.category}, Manufacturer: {self.manufacturer}, Product: {self.product}, "
              f"Version: {self.version}, Standard Size: {self.standard_size}")
        
    def get_header(self):
        return ['Category', 'Manufacturer', 'Product', 'Version', 'Standard Size']
    
    def get_content(self):
        return [self.category, self.manufacturer, self.product, self.version, self.standard_size]