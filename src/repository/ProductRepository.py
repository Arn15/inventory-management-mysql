def create_product(conn, manufacturer_id, category_id, product_name, standard_size, recipe_json):
    """
    Creates a new product for a manufacturer with a specific recipe.
    """
    try:
        cursor = conn.cursor(dictionary=True)

        # Validate category exists
        cursor.execute("SELECT COUNT(*) AS count FROM Category WHERE category_id = %s", 
                    (category_id,))
        row = cursor.fetchone()['count']
        if row is None or row == 0:
            raise ValueError(f"Category {category_id} does not exist")

        print(f"manufacturer_id: {manufacturer_id}, category_id: {category_id}, product_name: {product_name}, standard_size: {standard_size}, recipe_json: {recipe_json}")
        # Execute the stored procedure
        cursor.callproc("CreateProduct", [
            manufacturer_id,
            category_id,
            product_name,
            standard_size,
            recipe_json
        ])
        
        return {
            'status': 'success',
            'message': f'Created product "{product_name}" for manufacturer {manufacturer_id}'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error creating product: {str(e)}'
        }


def update_product(conn, manufacturer_id, product_id, standard_size, recipe_json):
    """
    Updates an existing product with new details and recipe.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Validate product exists
        cursor.execute("SELECT COUNT(*) AS Count FROM Products WHERE product_id = %s", 
                   (product_id,))
        if cursor.fetchone()['Count'] == 0:
            raise ValueError(f"Product {product_id} does not exist")

        # Execute the stored procedure
        cursor.callproc("UpdateProduct", [manufacturer_id, product_id, standard_size, recipe_json])

        return {
            'status': 'success',
            'message': f'Updated product ID: {product_id}'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error updating product: {str(e)}'
        }


def check_product_lot_conflicts(conn, product_lot_number):
    """
    Checks for conflicting ingredients in a specific product lot.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("warn_do_not_combine_in_product_lot", [product_lot_number])
        
        # Fetch results
        results = cursor.fetchall()
        
        # Format results for application use
        conflicts = []
        for row in results:
            conflicts.append({
                'ingredient_id': row['ingredient_id'],
                'conflicting_ingredient_name': row['conflicting_ingredient_name']
            })
            
        return conflicts

    except Exception as e:
        print(f"Error checking product lot conflicts: {e}")
        return []
    

def get_product_by_id(conn, product_id):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.execute("SELECT product_name FROM Products WHERE product_id = %s", (product_id,))
        # Fetch results
        results = cursor.fetchone()
        
        if results is None:
            return None
        else:
            return results['product_name']
    except Exception as e:
        print(f"Error retrieving products: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_product_inventory(conn, manufacturer_id, product_id):
    """
    Retrieves inventory information for a specific manufacturer/product combination.
    """
    try:
        cursor = conn.cursor()
        # Validate manufacturer exists
        cursor.execute("SELECT COUNT(*) FROM Manufacturer WHERE manufacturer_id = %s", 
                (manufacturer_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Manufacturer {manufacturer_id} does not exist")

        # Validate product exists
        cursor.execute("SELECT COUNT(*) FROM Products WHERE product_id = %s", 
                (product_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Product {product_id} does not exist")

        # Execute the stored procedure
        cursor.callproc("get_prod_on_hand", [manufacturer_id, product_id])
        
        # Fetch results
        results = cursor.fetchall()
        
        # Format results for application use
        inventory = []
        for row in results:
            inventory.append({
                'version': row['version'],
                'product_lot_number': row['product_lot_number'],
                'quantity': row['quantity']
            })
            
        return inventory

    except Exception as e:
        print(f"Error retrieving product inventory: {e}")
        return []
    

def trace_product_recall(conn, recall_item):
    """
    Identifies products affected by a recalled ingredient or lot.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("TraceRecall", [recall_item])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            result = stored[0].fetchall()
        else:
            return []
        # Format results for application use
        affected_products = []
        for row in result:
            affected_products.append({
                'product_lot_number': row['product_lot_number'],
                'expiration_date': row['expiration_date'],
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'manufacturer_name': row['manufacturer_name']
            })
            
        return affected_products

    except Exception as e:
        print(f"Error tracing product recall: {e}")
        return None


def get_product_types(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("BrowseProductTypes")
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            result = stored[0].fetchall()
        else:
            return []
        
        product_type_list = []
        for row in result:
            product_type_list.append({
                    'category': row['Category'],
                    'manufacturer': row['Manufacturer'],
                    'product': row['Product'],
                    'version': row['Version'],
                    'standard_size': row['Standard_Size']
                })
        return product_type_list

    except Exception as e:
        print(f"Error getting product types: {e}")
        return []