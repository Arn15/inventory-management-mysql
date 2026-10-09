from repository import UserRepository

def authenticate_user_and_get_role(conn, user_id):
    return UserRepository.authenticate_user(conn, user_id)