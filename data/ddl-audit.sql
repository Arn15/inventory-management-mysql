DELIMITER //

USE `InventoryManagement` //

-- ---------------------------------------------------------------------------
-- Audit triggers: record every data change made through the stored procedures.
-- USER() is the connecting database account (e.g. inv_supplier@...), even though
-- the procedures and triggers run with their definer's privileges.
-- @app_user is set by the application right after a successful login.
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS audit_ingredients_ins //
DROP TRIGGER IF EXISTS audit_supplier_ingredient_ins //
DROP TRIGGER IF EXISTS audit_supplier_ingredient_upd //
DROP TRIGGER IF EXISTS audit_ingredient_inventory_ins //
DROP TRIGGER IF EXISTS audit_ingredient_inventory_upd //
DROP TRIGGER IF EXISTS audit_products_ins //
DROP TRIGGER IF EXISTS audit_manufacturer_product_ins //
DROP TRIGGER IF EXISTS audit_recipe_ins //
DROP TRIGGER IF EXISTS audit_product_inventory_ins //
DROP TRIGGER IF EXISTS audit_product_inventory_upd //
DROP TRIGGER IF EXISTS audit_do_not_combine_ins //
DROP TRIGGER IF EXISTS audit_log_no_update //
DROP TRIGGER IF EXISTS audit_log_no_delete //

CREATE TRIGGER audit_ingredients_ins AFTER INSERT ON Ingredients FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Ingredients', NEW.ingredient_id,
            CONCAT('name=', NEW.name, '; compound=', NEW.isCompound));
END//

CREATE TRIGGER audit_supplier_ingredient_ins AFTER INSERT ON Supplier_Ingredient FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Supplier_Ingredient', NEW.supplier_ingredient_id,
            CONCAT('supplier=', NEW.supplier_id, '; ingredient=', NEW.ingredient_id, '; version=', NEW.version,
                   '; price_per_pack=', IFNULL(NEW.price_per_pack, 'NULL')));
END//

CREATE TRIGGER audit_supplier_ingredient_upd AFTER UPDATE ON Supplier_Ingredient FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'UPDATE', 'Supplier_Ingredient', NEW.supplier_ingredient_id,
            CONCAT('price_per_pack ', IFNULL(OLD.price_per_pack, 'NULL'), ' -> ', IFNULL(NEW.price_per_pack, 'NULL'),
                   '; pack_size ', IFNULL(OLD.pack_size, 'NULL'), ' -> ', IFNULL(NEW.pack_size, 'NULL')));
END//

CREATE TRIGGER audit_ingredient_inventory_ins AFTER INSERT ON Ingredient_Inventory FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Ingredient_Inventory', NEW.ingredient_lot_number,
            CONCAT('qty=', NEW.remaining_amt, '; unit_price=', NEW.unit_price, '; expires=', NEW.expiration_date));
END//

CREATE TRIGGER audit_ingredient_inventory_upd AFTER UPDATE ON Ingredient_Inventory FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'UPDATE', 'Ingredient_Inventory', NEW.ingredient_lot_number,
            CONCAT('remaining_amt ', OLD.remaining_amt, ' -> ', NEW.remaining_amt));
END//

CREATE TRIGGER audit_products_ins AFTER INSERT ON Products FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Products', NEW.product_id,
            CONCAT('name=', NEW.product_name, '; category=', NEW.cat_id));
END//

CREATE TRIGGER audit_manufacturer_product_ins AFTER INSERT ON Manufacturer_Product FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Manufacturer_Product', NEW.manufacturer_product_id,
            CONCAT('manufacturer=', NEW.manufacturer_id, '; product=', NEW.product_id,
                   '; version=', NEW.version, '; standard_size=', NEW.standard_size));
END//

CREATE TRIGGER audit_recipe_ins AFTER INSERT ON Recipe FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Recipe', NEW.recipe_id,
            CONCAT('mfg_product=', NEW.manufacturer_product_id, '; ingredient=', NEW.ingredient_id, '; qty=', NEW.quantity));
END//

CREATE TRIGGER audit_product_inventory_ins AFTER INSERT ON Product_Inventory FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Product_Inventory', NEW.product_lot_number,
            CONCAT('qty=', NEW.quantity, '; expires=', NEW.expiration_date));
END//

CREATE TRIGGER audit_product_inventory_upd AFTER UPDATE ON Product_Inventory FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'UPDATE', 'Product_Inventory', NEW.product_lot_number,
            CONCAT('quantity ', OLD.quantity, ' -> ', NEW.quantity));
END//

CREATE TRIGGER audit_do_not_combine_ins AFTER INSERT ON Do_Not_Combine FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (app_user, db_account, action, table_name, record_key, details)
    VALUES (@app_user, USER(), 'INSERT', 'Do_Not_Combine',
            CONCAT(NEW.ingredient_id_1, ',', NEW.ingredient_id_2), NULL);
END//

-- Append-only: the audit trail cannot be edited or deleted row by row, even by an admin.
CREATE TRIGGER audit_log_no_update BEFORE UPDATE ON Audit_Log FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Audit_Log is append-only';
END//

CREATE TRIGGER audit_log_no_delete BEFORE DELETE ON Audit_Log FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Audit_Log is append-only';
END//

DELIMITER ;
