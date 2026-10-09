class ProductIncompatibility:
    def __init__(self, ingredient_id_1, ingredient_1_name, ingredient_id_2, ingredient_2_name):
        self.ingredient_id_1 = ingredient_id_1
        self.ingredient_1_name = ingredient_1_name
        self.ingredient_id_2 = ingredient_id_2
        self.ingredient_2_name = ingredient_2_name
    
    def display(self):
        print(f"Ingredient A: {self.ingredient_1_name}, Ingredient B: {self.ingredient_2_name}")

    def get_header(self):
        return ['Ingredient A', 'Ingredient B']
    
    def get_content(self):
        return [self.ingredient_1_name, self.ingredient_2_name]