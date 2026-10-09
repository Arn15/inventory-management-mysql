class IngredientInventory:
    def __init__(self, ingredient_lot_number, supplier_ingredient_id, unit_price, pack_size, remaining_amt, 
                 expiration_date, creation_date, ingredient_batch_id):
        self.ingredient_lot_number = ingredient_lot_number
        self.supplier_ingredient_id = supplier_ingredient_id
        self.unit_price = unit_price
        self.pack_size = pack_size
        self.remaining_amt = remaining_amt
        self.expiration_date = expiration_date
        self.creation_date = creation_date
        self.ingredient_batch_id = ingredient_batch_id

    def display(self):
        print(f"Ingredient Lot Number: {self.ingredient_lot_number}, Unit Price: {self.unit_price}, Pack Size: {self.pack_size}",
              f"Remaining Amount: {self.remaining_amt}, Expiration Date: {self.expiration_date}, Creation Date: {self.creation_date}")