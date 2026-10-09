def insert_supplier(conn, supplier_name):
    """
    Registers a new supplier in the system.
    
    Parameters:
        supplier_name (str): Name of the supplier
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'message': Result message
        }
    """
    try:
        cursor = conn.cursor()
        # Check if supplier already exists
        cursor.execute("SELECT COUNT(*) FROM Supplier WHERE supplier_name = %s", 
                    (supplier_name,))
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Supplier '{supplier_name}' already exists")

        # Execute the stored procedure
        cursor.callproc("InsertSupplier", [supplier_name])
        conn.commit()
        
        return {
            'status': 'success',
            'message': f'Added supplier "{supplier_name}" to the system'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error adding supplier: {str(e)}'
        }
    
def get_supplier_by_user_id(conn, user_id):
    """
    Retrieves supplier information based on the associated user ID.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.execute("SELECT supplier_id, supplier_name, user_id FROM Supplier WHERE user_id = %s", (user_id,))
        
        result = cursor.fetchone()
        print(result)
        if result:
            return {
                'status': 'success',
                'supplier': {
                    'supplier_id': result['supplier_id'],
                    'supplier_name': result['supplier_name'],
                    'user_id': result['user_id']
                }
            }
        else:
            return {
                'status': 'error',
                'message': f'No supplier found for user ID {user_id}'
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving supplier: {str(e)}'
        }
    
def get_all_suppliers(conn):
    """
    Retrieves supplier information based on the associated user ID.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.execute("SELECT supplier_id, supplier_name, user_id FROM Supplier")
        
        result = cursor.fetchall()
        if result is None:
            return []
        suppliers = []

        for row in result:
            suppliers.append({
                    'supplier_id': row['supplier_id'],
                    'supplier_name': row['supplier_name'],
                    'user_id': row['user_id']
                })
        return suppliers
    except Exception as e:
        print(f"Error retrieving all suppliers: {str(e)}")
        return []
    
def get_supplier_spend(conn, manufacturer_id):
    """
    Retrieves total spend by supplier for a specific manufacturer.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("GetSupplierSpendByManufacturer", [manufacturer_id])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        # Format results for application use
        supplier_spend = []
        for row in results:
            supplier_spend.append({
                'supplier_id': row['supplier_id'],
                'supplier_name': row['supplier_name'],
                'total_spent': float(row['total_spent'])  # Convert decimal to float
            })
            
        return supplier_spend

    except Exception as e:
        print(f"Error retrieving supplier spend data: {str(e)}")
        return []