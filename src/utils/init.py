import os
from utils import ConfigReader, DBUtils

def run_db_init_script(conn, config, script, delimiter =";"):
    if config.get(script, {}).get("enabled", False):
        script_path = config.get(script, {}).get("location", "")

        if not script_path or not os.path.exists(script_path):
            print(f"SQL script not found at: {script_path}")
            return

        try:
            with open(script_path, "r") as file:
                sql_script = file.read()

            cursor = conn.cursor()

            sql_script = sql_script.replace("DELIMITER " + delimiter, "").replace("DELIMITER ;", "")
            statements = [stmt.strip() for stmt in sql_script.split(delimiter) if stmt.strip()]

            for stmt in statements:
                # print(f"Executing statement: {stmt}...")  # Print first 30 chars of the statement
                cursor.execute(stmt)

            conn.commit()
            cursor.close()

            print(f"Database initialized successfully using {script_path}")

        except Exception as e:
            print(f"Error initializing database, {script}: {e}")


def initialize_database():
    print("Initializing database...")
    config = ConfigReader.read_config("config/config.yaml", "database")
    if config is None:
        print("Failed to load configuration: database")
        return None
    
    conn = DBUtils.create_connection(config)
    if conn is None:
        print("Failed to establish database connection.")
        return None
    
    config = ConfigReader.read_config("config/config.yaml", "init")
    if config is None:
        print("Failed to load configuration: init")
        return None
    run_db_init_script(conn, config, "tables")
    run_db_init_script(conn, config, "triggers", "//")
    run_db_init_script(conn, config, "procedures", "$$")
    run_db_init_script(conn, config, "data") 
    return conn
    