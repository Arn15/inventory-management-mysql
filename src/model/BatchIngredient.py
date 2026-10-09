class BatchIngredient:
    def __init__(self, ingredient_lot_number, ingredient_name):
        self.ingredient_lot_number = ingredient_lot_number
        self.ingredient_name = ingredient_name

    def __repr__(self):
        return f"<Ingredient(id={self.ingredient_lot_number}, name={self.ingredient_name}>"
    
    def display(self):
        print(f"Ingredient Lot Number: {self.ingredient_lot_number}, Name: {self.ingredient_name}")

    def get_header(self):
        return ['Ingredient Lot Number', 'Ingredient Name']
    
    def get_content(self):
        return [self.ingredient_lot_number, self.ingredient_name]