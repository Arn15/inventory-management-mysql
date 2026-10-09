class Manufacturer:
    def __init__(self, manufacturer_id, manufacturer_name, user_id):
        self.manufacturer_id = manufacturer_id
        self.manufacturer_name = manufacturer_name
        self.user_id = user_id

    def __repr__(self):
        return f"<Manufacturer(id={self.manufacturer_id}, name={self.manufacturer_name}, user_id={self.user_id})>"
    