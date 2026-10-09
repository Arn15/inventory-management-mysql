class IngredientConflict:
    def __init__(self, ingredient_id, conflicting_ingredient_name):
        self.ingredient_id = ingredient_id
        self.conflicting_ingredient_name = conflicting_ingredient_name

    def get_header(self):
        return ['Conflicting Ingredient Name']
    
    def get_content(self):
        return [self.conflicting_ingredient_name]