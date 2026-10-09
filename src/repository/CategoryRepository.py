def insert_category(conn, category_name):
    """
    Registers a new product category in the system.
    
    Parameters:
        category_name (str): Name of the category (e.g., 'Dinners', 'Sides')
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'message': Result message
        }
    """
    try:
        cursor = conn.cursor()
        # Check if category already exists
        cursor.execute("SELECT COUNT(*) FROM Category WHERE category_name = %s", 
                    (category_name,))
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Category '{category_name}' already exists")

        # Execute the stored procedure
        cursor.callproc("InsertCategories", [category_name])
        conn.commit()
        
        return {
            'status': 'success',
            'message': f'Added category "{category_name}" to the system'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error adding category: {str(e)}'
        }
    
def get_all_categories(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Category")
        categories = cursor.fetchall()
        if categories is None:
            categories = [] # Return empty list if no categories found
        return {
                'status': 'success',
                'categories': categories
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving categories: {str(e)}'
        }