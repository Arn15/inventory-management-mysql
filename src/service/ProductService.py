from repository import ProductRepository
from model.Product import Product
from model.TraceRecall import TraceRecall
from model.BrowseProductType import BrowseProductType
from model.ManufacturerProduct import ManufacturerProduct
from datetime import datetime

def create_product(conn, manufacturer_id, category_id, product_name, standard_size, recipe_json):
    result = ProductRepository.create_product(conn, manufacturer_id, category_id,product_name, standard_size, recipe_json)
    print(result['message'])
    if result['status'] == 'success':
        return True
    return False

def update_product(conn, manufacturer_id, product_id, standard_size, recipe_json):
    result = ProductRepository.update_product(conn, manufacturer_id, product_id, standard_size, recipe_json)
    print(result['message'])
    if result['status'] == 'success':
        return True
    return False

def get_product_by_id(product_id):
    return ProductRepository.get_product_by_id(product_id)

def check_product_lot_conflicts(conn, product_lot_number):
    return ProductRepository.check_product_lot_conflicts(conn, product_lot_number)

def get_product_inventory(conn, manufacturer_id, product_id):
    return ProductRepository.get_product_inventory(conn, manufacturer_id, product_id)

def trace_product_recall(conn, recall_item):
    trace_recalls = ProductRepository.trace_product_recall(conn, recall_item)
    if trace_recalls == []:
        return []
    trace_recall_list = []
    for row in trace_recalls:
        trace_recall_list.append(TraceRecall(row['product_lot_number'], row['expiration_date'], row['product_id'], 
                                 row['product_name'], row['manufacturer_name']))
    return trace_recall_list

def get_product_types(conn):
    result = ProductRepository.get_product_types(conn)
    if result == []:
        return None
    product_type_list = []
    for row in result:
        product_type_list.append(BrowseProductType(row['category'], row['manufacturer'], 
                                                   row['product'], row['version'], row['standard_size']))
    return product_type_list
