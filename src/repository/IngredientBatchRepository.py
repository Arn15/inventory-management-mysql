def create_ingredient_batch(conn, supplier_id, ingredient_id, unit_price, pack_size, expiration_date):
    """
    Creates a new batch of an ingredient supplied by a specific supplier.
    
    Parameters:
        supplier_id (int): ID of the supplier
        ingredient_id (int): ID of the ingredient
        unit_price (float): Price per unit of the ingredient
        pack_size (int): Quantity in the batch
        expiration_date (date): Expiration date of the batch
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'message': Result message
        }
    """
    try:
        cursor = conn.cursor()
        # Verify supplier supplies this ingredient
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Supplier_Ingredient 
            WHERE supplier_id = %s AND ingredient_id = %s
        """, (supplier_id, ingredient_id))

        if cursor.fetchone()[0] == 0:
            raise ValueError("Supplier does not supply this ingredient")

        # Execute the stored procedure
        cursor.callproc("CreateIngredientBatch", [
            supplier_id,
            ingredient_id,
            unit_price,
            pack_size,
            expiration_date
        ])
        
        print(cursor.fetchall())
        return True

    except Exception as e:
        conn.rollback()
        return False

def get_all_ingredient_inventory(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ingredient_lot_number, supplier_ingredient_id, unit_price, pack_size, 
                    remaining_amt, expiration_date, creation_date, ingredient_batch_id
            FROM Ingredient_Inventory""")

        results = cursor.fetchall()

        if results is None:
            return []
        
        ingredient_inventory_list = []
        for row in results:
            ingredient_inventory_list.append({
                'ingredient_lot_number' : row['ingredient_lot_number'], 
                'supplier_ingredient_id' : row['supplier_ingredient_id'], 
                'unit_price' : row['unit_price'], 
                'pack_size' : row['pack_size'], 
                'remaining_amt' : row['remaining_amt'], 
                'expiration_date' : row['expiration_date'], 
                'creation_date' : row['creation_date'], 
                'ingredient_batch_id' : row['ingredient_batch_id']
            })

    except Exception as e:
        print(f"Error while retrieving ingredient inventory data: {e}")