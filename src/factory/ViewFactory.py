from view.ManufacturerView import ManufacturerView
from view.SupplierView import SupplierView
from view.ViewerView import ViewerView

def get_view(role_id):
    if role_id == 'MANUFACTURER':
        return ManufacturerView()
    elif role_id == 'SUPPLIER':
        return SupplierView()
    else:
        return ViewerView()