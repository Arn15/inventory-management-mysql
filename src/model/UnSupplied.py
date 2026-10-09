class UnSupplied:
    def __init__(self, manufacturer_id, manufacturer_name):
        self.manufacturer_id = manufacturer_id
        self.manufacturer_name = manufacturer_name

    def get_header(self):
        return ['Manufacturers Not Being Supplied']
    
    def get_content(self):
        return [self.manufacturer_name]