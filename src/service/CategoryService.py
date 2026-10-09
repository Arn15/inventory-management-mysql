from repository import CategoryRepository
from model.Category import Category

def insert_category(conn, category_name):
    return CategoryRepository.insert_category(conn, category_name)

def get_all_categories(conn):
    categories = CategoryRepository.get_all_categories(conn)
    if categories['status'] == 'success':
        category_list = []
        for data in categories['categories']:
            category_list.append(Category(data[0], data[1]))
        return category_list
    else:
        print("Failed to retrieve categories.", categories.get('message', ''))
        return []