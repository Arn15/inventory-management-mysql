class ExpiringIngredient:
    def __init__(self, ingredient_lot_number, expiration_date, remaining_amount, unit_price):
        self.ingredient_lot_number = ingredient_lot_number
        self.expiration_date = expiration_date
        self.remaining_amount = remaining_amount
        self.unit_price = unit_price

    def display(self):
        print(f"Ingredient Lot Number: {self.ingredient_lot_number}, Expiration Date: {self.expiration_date}"
              f", Remaining Amount: {self.remaining_amount}, Unit Price: {self.unit_price}")
        
    def get_header(self):
        return ['Ingredient Lot Number', 'Expiration Date', 'Remaining Amount', 'Unit Price']
    
    def get_content(self):
        return [self.ingredient_lot_number, self.expiration_date, self.remaining_amount, self.unit_price]