import datetime

# Python Pseudocode for Creating a Product Batch
def create_product_batch(conn, manufacturer_id, product_id, recipe_version, quantity):
    try:
        cursor = conn.cursor(dictionary=True)
        # Validate product version exists
        # cursor.execute("SELECT manufacturer_product_id FROM Manufacturer_Product WHERE manufacturer_id = %s AND product_id = %s AND version = %s", 
        #             (manufacturer_id, product_id, recipe_version))
        # manu_prod_id = cursor.fetchone()['manufacturer_product_id']

        # Deduct ingredient stock and create batch
        args = [manufacturer_id, product_id, recipe_version, quantity]
        cursor.callproc("CreateProductBatch", args)
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error creating product batch: {e}")
        return False


def get_product_batch_ingredients(conn, product_id, manufacturer_id):
    """
    Retrieves ingredients and their lot numbers for the latest batch of a product.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("get_ing_and_lot_no", [product_id, manufacturer_id])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        
        # Format results for application use
        ingredients = []
        for row in results:
            ingredients.append({
                'ingredient_lot_number': row['ingredient_lot_number'],
                'ingredient_name': row['ingredient_name']
            })
            
        return ingredients

    except Exception as e:
        # Handle specific error messages from the stored procedure
        if "No such product found for this manufacturer" in str(e):
            print("Error: Product not found for this manufacturer")
        elif "No batch found for this product" in str(e):
            print("Error: No batches found for this product")
        else:
            print(f"Error retrieving batch ingredients: {e}")
        
        return []
    

def evaluate_health_risk(conn, product_lot_number):
    """
    Evaluates whether a product batch contains conflicting ingredients.
    
    Parameters:
        product_lot_number (str): The lot number of the product batch to evaluate
    
    Returns:
        dict: {
            'status': 'safe' or 'risk',
            'message': Evaluation result message
        }
    """
    try:
        cursor = conn.cursor()
        # Execute the stored procedure
        cursor.callproc("EvaluateHealthRisk", [product_lot_number])
        
        # If no exception, batch is safe
        return {
            'status': 'safe',
            'message': f'No conflicting ingredients found in batch {product_lot_number}'
        }

    except Exception as e:
        # Check if this is our specific health risk error
        if "Health Risk Detected" in str(e):
            return {
                'status': 'risk',
                'message': f'Health risk detected in batch {product_lot_number}: '
                         f'Contains conflicting ingredients'
            }
        else:
            # Handle other unexpected errors
            return {
                'status': 'error',
                'message': f'Error evaluating batch {product_lot_number}: {str(e)}'
            }

def get_all_product_batches(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.execute("""SELECT product_lot_number, manufacturer_product_id, expiration_date, 
                       creation_date, quantity, product_batch_id FROM Product_Inventory""")
        # Fetch results
        results = cursor.fetchall()
        
        if results is None:
            return []
        else:
            product_inventory_list = []
            for row in results:
                product_inventory_list.append({
                    'product_lot_number': row['product_lot_number'],
                    'manufacturer_product_id': row['manufacturer_product_id'],
                    'expiration_date': row['expiration_date'],   # was eval(str(...)): code execution on DB data, and turned 2026-11-10 into 2005
                    'creation_date': row['creation_date'],
                    'quantity': row['quantity'],
                    'product_batch_id': row['product_batch_id']
                })
            return product_inventory_list
    except Exception as e:
        print(f"Error retrieving product batches: {e}")
        return []

def calculate_batch_unit_cost(conn, product_lot_number):
    """
    Calculates the unit cost of a product batch based on its ingredient costs.
    
    Parameters:
        product_lot_number (str): The lot number of the product batch
    
    Returns:
        float: Unit cost per item in the batch, or None if calculation failed
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("calc_product_batch_unit_cost", [product_lot_number])
        
         # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            result = stored[0].fetchall()
        else:
            return []
        
        if result:
            return float(result[0]['unit_cost'])
        else:
            print("No cost data found for this batch")
            return None

    except Exception as e:
        print(f"Error calculating batch cost: {e}")
        return None
    

def calculate_batch_cost(conn, prod_lot_num: str):
    """
    Calls the stored procedure `calc_batch_cost` to calculate the total cost
    of a product batch based on its lot number.

    Parameters:
        prod_lot_num (str): The product lot number.

    Returns:
        float | None: The total cost of the batch, or None if no result is found.
    """

    try:
        cursor = conn.cursor()
        cursor.callproc("calc_batch_cost", (prod_lot_num,))

        # Fetch the result
        result = cursor.fetchone()
        if result and 'total_cost' in result:
            return result['total_cost']
        else:
            return None

    except Exception as e:
        print(f"Database error: {e}")
        return None