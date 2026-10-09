class SupplierIngredient:
    def __init__(self, name, supplier_ingredient_id, supplier_id, ingredient_id, version):
        self.name = name
        self.supplier_ingredient_id = supplier_ingredient_id
        self.supplier_id = supplier_id
        self.ingredient_id = ingredient_id
        self.version = version

    def display(self):
        print(f"Ingredient Name: {self.name}, Version: {self.version}")