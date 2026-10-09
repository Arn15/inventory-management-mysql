import json


def create_supplier_ingredient(
        conn,
        supplier_id,
        ingredient_id,
        is_compound,
        material_list_json,
        price_per_pack,
        pack_size
):
    """
    Creates a new ingredient (atomic or compound) supplied by a specific supplier.
    
    Parameters:
        supplier_id (int): ID of the supplier
        ingredient_name (str): Name of the ingredient
        is_compound (bool): Whether this is a compound ingredient
        material_list_json (str): JSON string of component ingredients (for compound)
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'message': Result message
        }
    """
    try:
        cursor = conn.cursor()
        # Validate supplier exists
        cursor.execute("SELECT COUNT(*) FROM Supplier WHERE supplier_id = %s", 
                    (supplier_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Supplier {supplier_id} does not exist")

        # Execute the stored procedure
        cursor.callproc("CreateSupplierIngredient", [
            supplier_id,
            ingredient_id,
            is_compound,
            material_list_json,
            price_per_pack,
            pack_size
        ])
        
        conn.commit()
        return {
            'status': 'success',
            'message': f'Created ingredient "{ingredient_id}" with supplier {supplier_id}'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error creating ingredient: {str(e)}'
        }


def update_ingredient(conn, cur_supplier_id, cur_ing_id, new_material_list):
    """
    Calls the UpdateIngredient stored procedure to update an existing compound ingredient.

    Parameters:
        cur_supplier_id (int): ID of the supplier.
        cur_ing_id (str): ID of the ingredient to update.
        new_material_list (list of dict): List of ingredients in the new formulation, each with 'id' and 'qty'.

    Returns:
        dict: {
            'success': bool,
            'message': str
        }
    """
    try:
        cursor = conn.cursor()
        # Convert the new material list to a JSON string
        json_material = json.dumps(new_material_list)

        # Execute the stored procedure
        cursor.callproc("UpdateIngredient", [cur_supplier_id, cur_ing_id, json_material])

        return {
            'success': True,
            'message': 'Ingredient updated successfully'
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Error Updating Ingredient: {str(e)}"
        }
    

def get_supplier_ingredients(conn, supplier_id):
    """
    Retrieves all ingredients supplied by a specific supplier.
    
    Parameters:
        supplier_id (int): ID of the supplier to query
    
    Returns:
        List of dictionaries containing:
            - ingredient_name
    """
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.callproc("ViewSupplierIngredients", [supplier_id])

        ingredients = []

        # Stored procedures return results here
        for result in cursor.stored_results():
            rows = result.fetchall()

            for row in rows:
                ingredients.append({
                    'name': row['name'],
                    'supplier_ingredient_id': row['supplier_ingredient_id'],
                    'supplier_id': row['supplier_id'],
                    'ingredient_id': row['ingredient_id'],
                    'version': row['version']
                })

        return ingredients

    except Exception as e:
        print(f"Error retrieving supplier ingredients: {str(e)}")
        return []
    

def get_conflicting_ingredients(conn, product_lot_number):
    """
    Retrieves ingredients in a product lot that have conflicting combinations.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("GetConflictingIngredientsForProductLot", [product_lot_number])
        
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        # Format results for application use
        conflicts = []
        for row in results:
            conflicts.append({
                'ingredient_id': row['ingredient_id'],
                'conflicting_ingredient_name': row['conflicting_ingredient_name']
            })
            
        return conflicts

    except Exception as e:
        print(f"Error retrieving conflicting ingredients: {str(e)}")
        return []
    
def get_supplier_ingredients_complement(conn, supplier_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ingredient_id, name, isCompound
            FROM Ingredients
            WHERE ingredient_id NOT IN (
            SELECT DISTINCT ingredient_id
            FROM Supplier_Ingredient
            WHERE supplier_id = %s
            ); """, (supplier_id,))


        rows = cursor.fetchall()
        supplier_ingredients_complement = []
        for row in rows:
            supplier_ingredients_complement.append({
                'ingredient_id': row[0],
                'ingredient_name': row[1],
                'is_Compound': row[2]
            })
        return supplier_ingredients_complement
    
    except Exception as e:
        print(f"Error retrieving Ingredients the Supplier does not supply: {str(e)}")
        return []