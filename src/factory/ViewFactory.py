from view.ManufacturerView import ManufacturerView
from view.SupplierView import SupplierView
from view.ViewerView import ViewerView

_VIEWS = {"MANUFACTURER": ManufacturerView, "SUPPLIER": SupplierView, "VIEWER": ViewerView}


def get_view(role_id):
    # Fail closed: an unknown or missing role gets no view (previously it fell through to the
    # Viewer menu, so any typed-in user ID, even a non-existent one, got read access).
    if role_id not in _VIEWS:
        raise PermissionError(f"No view for role {role_id!r}")
    return _VIEWS[role_id]()
