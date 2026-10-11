"""Least-privilege grants for each application database account.

Every write goes through stored procedures, which run with their definer's rights
(SQL SECURITY DEFINER, the MySQL default). Application accounts therefore get:
  * EXECUTE on exactly the procedures their role's menu uses
  * SELECT on exactly the tables their role's screens read directly
  * no INSERT / UPDATE / DELETE on any table, no access to User or Audit_Log
The login account can read only the authentication columns of User, update only the
lockout columns, and append to Audit_Log.

These lists were derived from the view -> service -> repository call graph; tests/
checks that each role can run its procedures and nothing else.
"""

ROLE_GRANTS = {
    "MANUFACTURER": {
        "procedures": ["CreateProduct", "UpdateProduct", "CreateProductBatch", "TraceRecall",
                       "almost_expired_ing", "get_nearly_out_of_stock", "get_prod_on_hand"],
        "tables": ["Category", "Ingredient_Inventory", "Ingredients", "Manufacturer",
                   "Manufacturer_Product", "Products", "Supplier", "Supplier_Ingredient"],
    },
    "SUPPLIER": {
        "procedures": ["CreateIngredientBatch", "CreateSupplierIngredient", "InsertIngredient",
                       "ViewSupplierIngredients"],
        "tables": ["Ingredients", "Supplier", "Supplier_Ingredient"],
    },
    "VIEWER": {
        "procedures": ["BrowseProductTypes", "CompareProductIncompatibilities", "GenerateIngredientList",
                       "GetConflictingIngredientsForProductLot", "GetManufacturersNotSuppliedBySupplier",
                       "GetSupplierSpendByManufacturer", "calc_product_batch_unit_cost", "get_ing_and_lot_no"],
        "tables": ["Manufacturer", "Manufacturer_Product", "Product_Inventory", "Supplier"],
    },
}

AUTH_GRANTS = {
    "select_columns": ["user_id", "role_code", "password_hash", "failed_attempts", "locked_until"],
    "update_columns": ["failed_attempts", "locked_until", "last_login"],
    "insert_tables": ["Audit_Log"],
}


def grant_statements(db: str, account: str, role: str) -> list[str]:
    """GRANT statements for one account (account is a quoted 'user'@'host' string)."""
    stmts = [f"GRANT USAGE ON *.* TO {account}"]
    if role == "AUTH":
        sel = ", ".join(AUTH_GRANTS["select_columns"])
        upd = ", ".join(AUTH_GRANTS["update_columns"])
        stmts.append(f"GRANT SELECT ({sel}), UPDATE ({upd}) ON `{db}`.`User` TO {account}")
        stmts += [f"GRANT INSERT ON `{db}`.`{t}` TO {account}" for t in AUTH_GRANTS["insert_tables"]]
        return stmts
    g = ROLE_GRANTS[role]
    stmts += [f"GRANT SELECT ON `{db}`.`{t}` TO {account}" for t in g["tables"]]
    stmts += [f"GRANT EXECUTE ON PROCEDURE `{db}`.`{p}` TO {account}" for p in g["procedures"]]
    return stmts
