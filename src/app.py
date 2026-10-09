from utils import init
from service import LoginService
from factory import ViewFactory

def main():
    # Example usage of the database functions
    conn = init.initialize_database()
    if conn:
        print("Database connection established successfully.")
        user_id = input("Enter your user_id: ")
        role = LoginService.authenticate_user_and_get_role(conn, user_id)
        print(f"Authenticated user role: {role}")
        view = ViewFactory.get_view(role)
        view.run(conn, user_id)
        conn.close()

if __name__ == "__main__":
    main()