from repository import SupplierRepository
from model.Supplier import Supplier
from model.ManufacturerSpentOnSupplier import ManufacturerSpentOnSupplier

def insert_supplier(conn, supplier_name):
    return SupplierRepository.insert_supplier(conn, supplier_name)

def get_supplier_by_user_id(conn, user_id):
    result = SupplierRepository.get_supplier_by_user_id(conn, user_id)
    if result['status'] == 'success':
        return Supplier(
            result['supplier']['supplier_id'],
            result['supplier']['supplier_name'],
            result['supplier']['user_id']
        )
    else:
        return None
    
def get_supplier_spend(conn, manufacturer_id):
    supplier_spent = SupplierRepository.get_supplier_spend(conn, manufacturer_id)
    if supplier_spent == []:
        return None
    supplier_spent_list = []
    for row in supplier_spent:
        supplier_spent_list.append(ManufacturerSpentOnSupplier(row['supplier_id'], row['supplier_name'], row['total_spent']))
    return supplier_spent_list

def get_all_suppliers(conn):
    suppliers = SupplierRepository.get_all_suppliers(conn)
    if suppliers == []:
        return None
    suppliers_list = []
    for row in suppliers:
        suppliers_list.append(Supplier(row['supplier_id'], row['supplier_name'], row['user_id']))
    return suppliers_list