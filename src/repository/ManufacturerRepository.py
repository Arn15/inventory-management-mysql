def insert_manufacturer(conn, manufacturer_name):
    """
    Registers a new manufacturer in the system.
    
    Parameters:
        manufacturer_name (str): Name of the manufacturer
    
    Returns:
        dict: {
            'status': 'success' or 'error',
            'message': Result message
        }
    """
    try:
        cursor = conn.cursor()
        # Check if manufacturer already exists
        cursor.execute("SELECT COUNT(*) FROM Manufacturer WHERE manufacturer_name = %s", 
                    (manufacturer_name,))
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Manufacturer '{manufacturer_name}' already exists")

        # Execute the stored procedure
        cursor.callproc("InsertManufacturer", [manufacturer_name])
        conn.commit()
        
        return {
            'status': 'success',
            'message': f'Added manufacturer "{manufacturer_name}" to the system'
        }

    except Exception as e:
        conn.rollback()
        return {
            'status': 'error',
            'message': f'Error adding manufacturer: {str(e)}'
        }

def get_manufacturer_by_user_id(conn, user_id):
    """
    Retrieves manufacturer details based on the associated user ID.

    Parameters:
        user_id (int): ID of the user

    Returns:
        dict: Manufacturer details or error message
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Manufacturer WHERE user_id = %s", (user_id,))
        manufacturer = cursor.fetchone()
        if manufacturer:
            return {
                'status': 'success',
                'manufacturer': manufacturer
            }
        else:
            return {
                'status': 'error',
                'message': 'Manufacturer not found for the given user ID'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving manufacturer: {str(e)}'
        }
    
def get_all_manufacturers(conn):
    """
    Retrieves all manufacturer details.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT manufacturer_id, manufacturer_name, user_id FROM Manufacturer")
        manufacturers = cursor.fetchall()
        if manufacturers is None:
            return []
        manufacturer_list = []
        for manufacturer in manufacturers:
            manufacturer_list.append({
                'manufacturer_id' : manufacturer['manufacturer_id'], 
                'manufacturer_name' : manufacturer['manufacturer_name'], 
                'user_id' : manufacturer['user_id']
            })
        return manufacturer_list
    except Exception as e:
        print(f"Error getting all manufacturers: {e}")
        return []
    