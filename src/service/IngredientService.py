from repository import IngredientRepository
from model.Ingredient import Ingredient
from model.IngredientList import IngredientList


def validate_ingredients_list(conn, recipe_json):
    return IngredientRepository.validate_ingredients_list(conn, recipe_json)

def add_do_not_combine(conn, ingredient_id_1: int, ingredient_id_2: int):
    return IngredientRepository.add_do_not_combine(conn, ingredient_id_1, ingredient_id_2)

def create_new_ingredient(conn, ingredient_name, is_compound):
    return IngredientRepository.create_new_ingredient(conn, ingredient_name, is_compound)

def get_all_ingredients(conn):
    ingredients = IngredientRepository.get_all_ingredients(conn)
    if ingredients is None:
        return None
    ingredient_list = []
    for data in ingredients:
        ingredient_list.append(Ingredient(data['ingredient_id'], data['ingredient_name'], data['is_compound']))
    return ingredient_list
    

def get_all_ingredient_lots(conn):
    ingredients = IngredientRepository.get_all_ingredient_lots(conn)
    if ingredients is None:
        return None
    ingredient_list = []
    for data in ingredients:
        ingredient_list.append({"ingredient_lot_number": data['ingredient_lot_number'],"ingredient_name": data['ingredient_name'],"supplier_name": data['supplier_name']})
    return ingredient_list

def get_ingredient_by_id(conn, ingredient_id):
    data = IngredientRepository.get_ingredient_by_id(conn, ingredient_id)
    if data is None:
        return None
    return Ingredient(data['ingredient_id'], data['ingredient_name'], data['is_compound'])

def get_ingredient_list(conn, product_lot_number):
    result = IngredientRepository.get_ingredient_list(conn, product_lot_number)
    if result == []:
        return None
    ingredient_list = []
    for row in result:
        ingredient_list.append(IngredientList(row['ingredient_id'], row['ingredient_name'], row['qty_from_recipe']))
    return ingredient_list