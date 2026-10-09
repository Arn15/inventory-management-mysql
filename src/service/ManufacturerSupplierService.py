from repository import ManufacturerSupplierRepository
from model.UnSupplied import UnSupplied

def get_manufacturers_not_supplied_by_supplier(conn, supplier_id):
    not_supplied = ManufacturerSupplierRepository.get_manufacturers_not_supplied_by_supplier(conn, supplier_id)
    if not_supplied == []:
        return None
    not_supplied_list = []
    for row in not_supplied:
        not_supplied_list.append(UnSupplied(row['manufacturer_id'], row['manufacturer_name']))
    return not_supplied_list