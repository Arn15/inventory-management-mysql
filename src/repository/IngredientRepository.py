def validate_ingredients_list(conn, recipe_json):
    """
    Validates a recipe for "Do Not Combine" conflicts.
    """
    try:
        # Execute the stored procedure
        cursor = conn.cursor()
        cursor.callproc("validate_ingredients_list", [recipe_json, "valid"])
        result = cursor.fetchone()
        
        if result and result['valid']:
            return {
                'valid': True,
                'message': 'Recipe contains no conflicting ingredients'
            }
        else:
            return {
                'valid': False,
                'message': 'Recipe contains conflicting ingredients combinations'
            }

    except Exception as e:
        return {
            'valid': False,
            'message': f'Error validating recipe: {str(e)}'
        }
    
def create_new_ingredient(conn, ingredient_name, is_compound):
    try:
        cursor = conn.cursor()
        # Call the stored procedure
        cursor.callproc("InsertIngredient", (ingredient_name, is_compound))

    except Exception as err:
        return {
            'valid': False,
            'message': f'Error inserting ingredients to do not combine list: {str(err)}'
        }
    

def add_do_not_combine(conn, ingredient_id_1: int, ingredient_id_2: int):
    """
    Calls the stored procedure `AddDoNotCombineIngredients` to add a pair of ingredients
    that should not be combined.
    """
    try:
        cursor = conn.cursor()
        # Call the stored procedure
        cursor.callproc("AddDoNotCombineIngredients", (ingredient_id_1, ingredient_id_2))

    except Exception as err:
        return {
            'valid': False,
            'message': f'Error inserting ingredients to do not combine list: {str(err)}'
        }
    
def get_all_ingredients(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ingredient_id, name, isCompound FROM Ingredients")
        results = cursor.fetchall()
        
        if results is None:
            return None
        
        ingredients = []
        for row in results:
            ingredients.append({
                'ingredient_id': row['ingredient_id'],
                'ingredient_name': row['name'],
                'is_compound': row['isCompound']
            })
        
        return ingredients
    except Exception as e:
        print(f"Error retrieving ingredients: {e}")
        return None
    
def get_all_ingredient_lots(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ii.ingredient_lot_number, ing.name AS ingredient_name, s.supplier_name FROM Ingredient_Inventory ii JOIN Supplier_Ingredient si ON ii.supplier_ingredient_id = si.supplier_ingredient_id JOIN Ingredients ing ON si.ingredient_id = ing.ingredient_id JOIN Supplier s ON si.supplier_id = s.supplier_id;")
        results = cursor.fetchall()
        if results == []:
            return None
        
        ingredients = []
        for row in results:
            ingredients.append({
                'ingredient_lot_number': row['ingredient_lot_number'],
                'ingredient_name': row['ingredient_name'],
                'supplier_name': row['supplier_name']
            })
        
        return ingredients
    except Exception as e:
        print(f"Error retrieving ingredients: {e}")
        return None
    
def get_ingredient_by_id(conn, ingredient_id):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ingredient_id, name, isCompound FROM Ingredients WHERE ingredient_id = %s", 
                       (ingredient_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None
        
        else:
            return {
                'ingredient_id': result['ingredient_id'],
                'ingredient_name': result['name'],
                'is_compound': result['isCompound']
                }

    except Exception as e:
        return None
    
def get_ingredient_list(conn, product_lot_number):
    try:
        cursor = conn.cursor(dictionary=True)
        print(product_lot_number)
        cursor.callproc("GenerateIngredientList", [product_lot_number])
        # Fetch results
        stored = list(cursor.stored_results())
        print(stored)
        if stored and stored[0].with_rows:
            # Check if the first result set has rows to fetch
            result = stored[0].fetchall() 
        else:
            return []
        ingredient_list = []
        for row in result:
            ingredient_list.append({
                'ingredient_id': row['ingredient_id'],
                'ingredient_name': row['ingredient_name'],
                'qty_from_recipe': float(row['qty_from_recipe'])
                })
        return ingredient_list

    except Exception as e:
        print(f"Error retrieving ingredient list: {e}")
        return []