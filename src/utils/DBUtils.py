# database_utils.py
import mysql.connector
from mysql.connector import Error

def create_connection(config=None):
    """ Create a database connection """
    print("Establishing database connection...")
    try:
        conn = mysql.connector.connect(
            host=config.get("host", "localhost") if config else "localhost",
            port=config.get("port", 3306) if config else 3306,
            user=config.get("username", "root") if config else "root",
            password=config.get("password", "") if config else "",
            database=config.get("database", "InventoryManagement") if config else "InventoryManagement"
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_stored_procedure(conn, proc_name, params=None):
    """ Execute a stored procedure with given parameters """
    try:
        cursor = conn.cursor()
        if params:
            cursor.callproc(proc_name, params)
        else:
            cursor.callproc(proc_name)
        conn.commit()
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
        return results
    except Error as e:
        print(f"Error executing stored procedure: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()

def get_data_from_table(conn, table_name, conditions=None):
    """ Retrieve data from a specific table with optional conditions """
    try:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error retrieving data: {e}")
        return None
    finally:
        cursor.close()


# Example: Process order with trigger validation
def process_order(conn, user_id, product_id, quantity):
    results = execute_stored_procedure(conn, "ValidateInventory", [product_id, quantity])
    if results and results[0][0]['has_stock']:
        execute_stored_procedure(conn, "PlaceOrder", [user_id, product_id, quantity])
        print("Order placed successfully")
    else:
        print("Insufficient stock")