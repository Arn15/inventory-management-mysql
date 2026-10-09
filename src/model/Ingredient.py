class Ingredient:
    def __init__(self, ingredient_id, ingredient_name, is_compound):
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.is_compound = is_compound

    def __repr__(self):
        return f"<Ingredient(id={self.ingredient_id}, name={self.ingredient_name}, compound={self.is_compound})>"
    
    def display(self):
        print(f"Ingredient ID: {self.ingredient_id}, Name: {self.ingredient_name}")
        