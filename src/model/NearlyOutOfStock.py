class NearlyOutOfStock:
    def __init__(self, ingredient_name, ingredient_lot_number, remaining_amount, required_amount_for_batch):
        self.ingredient_name = ingredient_name
        self.ingredient_lot_number = ingredient_lot_number
        self.remaining_amount = remaining_amount
        self.required_amount_for_batch = required_amount_for_batch

    def display(self):
        print(f"Ingredient Name: {self.ingredient_name}, Ingredient Lot Number: {self.ingredient_lot_number}, "
              f"Remaining Amount: {self.remaining_amount}, Reguired Amount for batch: {self.required_amount_for_batch}")
        
    def get_header(self):
        return ['Ingredient Name', 'Product Lot Number', 'Quantity', 'Reguired Amount for batch']
    
    def get_content(self):
        return [self.ingredient_name, self.ingredient_lot_number, self.remaining_amount, self.required_amount_for_batch]