from repository import ManufacturerRepository
from model.Manufacturer import Manufacturer

def insert_manufacturer(conn, manufacturer_name):
    return ManufacturerRepository.insert_manufacturer(conn, manufacturer_name)

def get_manufacturer_by_user_id(conn, user_id):
    manufacturer_data = ManufacturerRepository.get_manufacturer_by_user_id(conn, user_id)
    if manufacturer_data['status'] == 'success':
        data = manufacturer_data['manufacturer']
        return Manufacturer(data[0], data[1], data[2])
    else:
        return None
    
def get_all_manufacturers(conn):
    result = ManufacturerRepository.get_all_manufacturers(conn)
    if result == []:
        return None
    manufacturer_list = []
    for row in result:
        manufacturer_list.append(Manufacturer(row['manufacturer_id'], row['manufacturer_name'], row['user_id']))
    return manufacturer_list