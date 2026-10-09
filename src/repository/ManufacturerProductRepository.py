from repository import ProductRepository

def check_low_stock(conn, manufacturer_product_id):
    """
    Checks for ingredients that are nearly out of stock for a specific manufacturer/product combination.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("get_nearly_out_of_stock", [manufacturer_product_id])
        
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        
        # Format results for application use
        low_stock_ingredients = []
        for row in results:
            low_stock_ingredients.append({
                'ingredient_name': row['name'],
                'ingredient_lot_number': row['ingredient_lot_number'],
                'remaining_amount': row['remaining_amt'],
                'required_amount_for_batch': row['required_amt']
            })
            
        return { 
                'status': 'success',
                'products': low_stock_ingredients }

    except Exception as e:
        print(f"Error checking inventory levels: {e}")
        return []
    
def get_all_products_by_manufacturer_id(conn, manufacturer_id):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.execute("SELECT manufacturer_product_id, manufacturer_id, product_id, version,standard_size " +
                        "FROM Manufacturer_Product WHERE manufacturer_id = %s", (manufacturer_id,))
        # Fetch results
        results = cursor.fetchall()
        
        if results is None:
            return []
        else:
            products = []
            for row in results:
                product_name = ProductRepository.get_product_by_id(conn, row['product_id'])
                products.append({
                    "manufacturer_product_id": row['manufacturer_product_id'],
                    "manufacturer_id": row['manufacturer_id'],
                    "product_id": row['product_id'],
                    "product_name": product_name,
                    "version": row['version'],
                    "standard_size": row['standard_size']
                })
                
            return { 
                'status': 'success',
                'products': products }
    except Exception as e:
        print(f"Error retrieving products: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
    
def get_on_hand_report_of_product(conn, manufacturer_id, product_id):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("get_prod_on_hand", [manufacturer_id, product_id])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []

        on_hand = []
        for result in results:
            on_hand.append({
                'version' : result['version'],
                'product_lot_number' : result['product_lot_number'],
                'quantity' : result['quantity']
            })
        return on_hand
    except Exception as e:
        print(f"Error retrieving on hand report: {e}")
        return []
    

def check_expiring_ingredients(conn, days_threshold=7):
    """
    Identifies ingredients that will expire within a specified number of days.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure with threshold
        cursor.callproc("almost_expired_ing", [days_threshold])

        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        
        # Format results for application use
        expiring_ingredients = []
        for row in results:
            expiring_ingredients.append({
                'ingredient_lot_number': row['ingredient_lot_number'],
                'expiration_date': row['expiration_date'].strftime('%Y-%m-%d'),
                'remaining_amount': row['remaining_amt'],
                'unit_price': row['unit_price']
            })
            
        return {
            'status' : 'success',
            'ingredients' : expiring_ingredients
        }

    except Exception as e:
        print(f"Error checking expiration dates: {str(e)}")
        return []
    
def get_product_incompatibilities(conn, manufacturer_product_id_1, manufacturer_product_id_2):
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure with threshold
        cursor.callproc("CompareProductIncompatibilities", [manufacturer_product_id_1, manufacturer_product_id_2])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            result = stored[0].fetchall()
        else:
            return []
        
        product_incompatibilities = []
        for row in result:
            product_incompatibilities.append({
                'ingredient_id_1': row['ingredient_id_1'],
                'ingredient_1_name': row['ingredient_1_name'],
                'ingredient_id_2': row['ingredient_id_2'],
                'ingredient_2_name': row['ingredient_2_name']
            })
            
        return product_incompatibilities

    except Exception as e:
        print(f"Error checking expiration dates: {str(e)}")
        return []