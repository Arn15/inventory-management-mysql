from repository import ManufacturerProductRepository
from model.ManufacturerProduct import ManufacturerProduct
from model.ExpiringIngredient import ExpiringIngredient
from model.OnHandReport import OnHandReport
from model.NearlyOutOfStock import NearlyOutOfStock
from model.ProductIncompatibility import ProductIncompatibility


def check_low_stock(conn, manufacturer_product_id):
    low_stock = ManufacturerProductRepository.check_low_stock(conn, manufacturer_product_id)
    if low_stock['status'] == 'success':
        low_stock_list = []
        for data in low_stock['products']:
            low_stock_list.append({
                "ingredient_name": data['ingredient_name'],
                "ingredient_lot_number": data['ingredient_lot_number'],
                "remaining_amount": data['remaining_amount'],
                "required_amount_for_batch": data['required_amount_for_batch']
            })
        return low_stock_list
    else:
        return []

def get_all_products_by_manufacturer(conn, manufacturer_id):
    products = ManufacturerProductRepository.get_all_products_by_manufacturer_id(conn, manufacturer_id)
    if products['status'] == 'success':
        product_list = []
        for data in products['products']:
            product_list.append(ManufacturerProduct(
                data['manufacturer_product_id'],
                data['manufacturer_id'],
                data['product_id'],
                data['product_name'],
                data['version'],
                data['standard_size']
            ))
        return product_list
    else:
        return []
    
def get_on_hand_report_of_product(conn, manufacturer_id, product_id):
    report = ManufacturerProductRepository.get_on_hand_report_of_product(conn, manufacturer_id, product_id)
    if report != []:
        return report
    else:
        return None
    
def check_expiring_ingredients(conn, days_threshold=7):
    ingredients = ManufacturerProductRepository.check_expiring_ingredients(conn, days_threshold)
    if ingredients['status'] == 'success':
        ingredient_list = []
        for data in ingredients['ingredients']:
            ingredient_list.append(ExpiringIngredient(
                data['ingredient_lot_number'],
                data['expiration_date'],
                data['remaining_amount'],
                data['unit_price']
            ))
        return ingredient_list
    else:
        return []
    
def get_product_incompatibilities(conn, manufacturer_product_id_1, manufacturer_product_id_2):
    resuts = ManufacturerProductRepository.get_product_incompatibilities(conn,
                                                                        manufacturer_product_id_1,
                                                                        manufacturer_product_id_2)
    if resuts == []:
        return None
    product_incompatibilities = []
    for row in resuts:
        product_incompatibilities.append(
            ProductIncompatibility(row['ingredient_id_1'], row['ingredient_1_name'], row['ingredient_id_2'], row['ingredient_2_name'])
        )
    return product_incompatibilities