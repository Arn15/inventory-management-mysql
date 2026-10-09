from repository import SupplierIngredientRepository
from model.SupplierIngredient import SupplierIngredient
from model.Ingredient import Ingredient
from model.IngredientConflict import IngredientConflict

def create_supplier_ingredient(conn, supplier_id, ingredient_id, is_compound, material_list_json, price_per_pack, pack_size):
    result = SupplierIngredientRepository.create_supplier_ingredient(
        conn, supplier_id, ingredient_id, is_compound, material_list_json, price_per_pack, pack_size)
    print(result['message'])
    if result['status'] == 'success':
        return True
    return False

def update_ingredient(conn, cur_supplier_id, cur_ing_id, new_material_list):
    return SupplierIngredientRepository.update_ingredient(conn, cur_supplier_id, cur_ing_id, new_material_list)

def add_supplier_ingredient(conn, supplier_id, ingredient_id):
    return SupplierIngredientRepository.add_supplier_ingredient(conn, supplier_id, ingredient_id)

def get_supplier_ingredients(conn, supplier_id):
    supplier_ingredients = SupplierIngredientRepository.get_supplier_ingredients(conn, supplier_id)
    if supplier_ingredients == []:
        return []
    supplier_ingrdient_list = []
    for ingredient in supplier_ingredients:
        supplier_ingrdient_list.append(SupplierIngredient(
            ingredient['name'], ingredient['supplier_ingredient_id'], ingredient['supplier_id'], 
            ingredient['ingredient_id'], ingredient['version']
        ))
    return supplier_ingrdient_list


def get_conflicting_ingredients(conn, product_lot_number):
    conflict_ingredients = SupplierIngredientRepository.get_conflicting_ingredients(conn, product_lot_number)
    if conflict_ingredients == []:
        return None
    conflict_ingredients_list = []
    for row in conflict_ingredients:
        conflict_ingredients_list.append(IngredientConflict(row['ingredient_id'], row['conflicting_ingredient_name']))
    return conflict_ingredients_list

def get_supplier_ingredients_compliment(conn, supplier_id):
    supplier_ingredients_compliment = SupplierIngredientRepository.get_supplier_ingredients_complement(conn, supplier_id)
    
    if supplier_ingredients_compliment == []:
        return []
    
    supplier_ingredients_compliment_list = []

    for result in supplier_ingredients_compliment:
        supplier_ingredients_compliment_list.append(Ingredient(result["ingredient_id"], result["ingredient_name"], result["is_Compound"]))

    return supplier_ingredients_compliment_list