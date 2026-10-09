class IngredientList:
    def __init__(self, ingredient_id, ingredient_name, qty_from_recipe):
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.qty_from_recipe = qty_from_recipe

    def display(self):
        print(f"Ingredient Name: {self.ingredient_name}, Quantity From Recipe: {self.qty_from_recipe}")

    def get_header(self):
        return ['Ingredient Name', 'Quantity From Recipe']
    
    def get_content(self):
        return [self.ingredient_name, self.qty_from_recipe]