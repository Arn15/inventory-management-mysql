from repository import ProductBatchRepository
from model.ProductInventory import ProductInventory 
from model.BatchIngredient import BatchIngredient
from datetime import datetime


def create_product_batch(conn, manufacturer_id, product_id, recipe_version, quantity):
    return ProductBatchRepository.create_product_batch(conn, manufacturer_id, product_id, recipe_version, quantity)


def get_product_batch_ingredients(conn, product_id, manufacturer_id):
    batch_ingredients = ProductBatchRepository.get_product_batch_ingredients(conn, product_id, manufacturer_id)
    if batch_ingredients == []:
        return None
    batch_ingredients_list = []
    for row in batch_ingredients:
        batch_ingredients_list.append(BatchIngredient(row['ingredient_lot_number'], row['ingredient_name']))
    return batch_ingredients_list

def evaluate_health_risk(conn, product_lot_number):
    return ProductBatchRepository.evaluate_health_risk(conn, product_lot_number)

def get_all_product_batches(conn):
    result = ProductBatchRepository.get_all_product_batches(conn)
    if result == []:
        return None
    product_inventory_list = []
    for row in result:
        product_inventory_list.append(ProductInventory(row['product_lot_number'], row['manufacturer_product_id'], row['expiration_date'], 
                                                       row['creation_date'], row['quantity'], row['product_batch_id']))
    return product_inventory_list

def calculate_batch_unit_cost(conn, product_lot_number):
    return ProductBatchRepository.calculate_batch_unit_cost(conn, product_lot_number)
    

def calculate_batch_cost(conn, prod_lot_num: str):
    return ProductBatchRepository.calculate_batch_cost(conn, prod_lot_num)