DELIMITER //

USE `InventoryManagement` //

DROP TRIGGER IF EXISTS validate_ingredient_formulation //

DROP TRIGGER IF EXISTS allow_atomic_in_dnc //

DROP TRIGGER IF EXISTS before_insert_ing_lot //

DROP TRIGGER IF EXISTS validate_ing_batch_expiry //

DROP TRIGGER IF EXISTS compute_ing_formulation_version //

DROP TRIGGER IF EXISTS compute_product_version //

DROP TRIGGER IF EXISTS before_insert_product_lot //

DROP TRIGGER IF EXISTS validate_product_lot_quantity //

DROP TRIGGER IF EXISTS update_expiration_date //


CREATE TRIGGER validate_ingredient_formulation
BEFORE INSERT ON Ingredient_Formulation
FOR EACH ROW
BEGIN
    DECLARE compound_flag BOOLEAN;

    SELECT isCompound INTO compound_flag
    FROM Ingredients
    WHERE ingredient_id = NEW.ingredient_id;

    IF compound_flag IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid ingredient_id: no such ingredient exists';
    ELSEIF compound_flag = TRUE THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'New compound ingredient must not have other compound ingredients in its formulation';
    END IF;
END//

CREATE TRIGGER before_insert_ing_lot
BEFORE INSERT ON Ingredient_Inventory
FOR EACH ROW
BEGIN
    DECLARE sup_id INT;
    DECLARE ing_id INT;
    DECLARE batch_count INT;

    SELECT supplier_id, ingredient_id INTO sup_id, ing_id
    FROM Supplier_Ingredient
    WHERE supplier_ingredient_id = NEW.supplier_ingredient_id;

    SELECT COUNT(*) INTO batch_count
    FROM Ingredient_Inventory
    WHERE supplier_ingredient_id = NEW.supplier_ingredient_id;
      
    SET NEW.ingredient_lot_number = CONCAT('I', ing_id, '-', 'S', sup_id, '-', 'B', (batch_count + 1));
    SET NEW.ingredient_batch_id = (batch_count + 1);
END//

CREATE TRIGGER validate_ing_batch_expiry
BEFORE INSERT ON Ingredient_Inventory
FOR EACH ROW
BEGIN
    IF DATEDIFF(NEW.expiration_date, CURDATE()) < 90 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ingredient batch expiration date must be at least 90 days from today';
    END IF;
END//

CREATE TRIGGER compute_ing_formulation_version
BEFORE INSERT ON Supplier_Ingredient
FOR EACH ROW
BEGIN
    DECLARE is_compound_ing BOOLEAN DEFAULT FALSE;
    DECLARE version_count INT DEFAULT 0;

    SELECT isCompound INTO is_compound_ing
    FROM Ingredients
    WHERE ingredient_id = NEW.ingredient_id;

    SELECT COUNT(*) INTO version_count 
    FROM Supplier_Ingredient
    WHERE supplier_id = NEW.supplier_id AND ingredient_id = NEW.ingredient_id;

    IF NOT is_compound_ing AND version_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Multiple ingredient formulations/versions allowed only for compound ingredients';
    END IF;

    SET NEW.version = version_count + 1;
END//


CREATE TRIGGER compute_product_version
BEFORE INSERT ON Manufacturer_Product
FOR EACH ROW
BEGIN
    DECLARE version_count INT DEFAULT 0;

    SELECT COUNT(*) INTO version_count 
    FROM Manufacturer_Product
    WHERE manufacturer_id = NEW.manufacturer_id AND product_id = NEW.product_id;

    SET NEW.version = version_count + 1;
END//


CREATE TRIGGER before_insert_product_lot
BEFORE INSERT ON Product_Inventory
FOR EACH ROW
BEGIN
  DECLARE lot_number varchar(255);
  DECLARE batch_count INT DEFAULT 0;

  SELECT COUNT(*) INTO batch_count
  FROM Product_Inventory
  WHERE manufacturer_product_id = NEW.manufacturer_product_id;

  CALL computeProductLotNumber(NEW.manufacturer_product_id, lot_number);
  SET NEW.product_lot_number = lot_number;
  SET NEW.product_batch_id = (batch_count + 1);

END//


CREATE TRIGGER validate_product_lot_quantity
BEFORE INSERT ON Product_Inventory
FOR EACH ROW
BEGIN
    DECLARE standard_batch_size INT;

    SELECT standard_size INTO standard_batch_size
    FROM Manufacturer_Product
    WHERE manufacturer_product_id = NEW.manufacturer_product_id;

    IF (NEW.quantity % standard_batch_size) != 0 THEN
        SIGNAL SQLSTATE '45001'
            SET MESSAGE_TEXT = 'Product lot size must a multiple of standard batch size';
    END IF;
END//

CREATE TRIGGER allow_atomic_in_dnc
BEFORE INSERT ON Do_Not_Combine
FOR EACH ROW
BEGIN
    DECLARE is_compound_ing_1 INT;
    DECLARE is_compound_ing_2 INT;

    SELECT isCompound INTO is_compound_ing_1
    FROM Ingredients
    WHERE ingredient_id = NEW.ingredient_id_1;

    SELECT isCompound INTO is_compound_ing_2
    FROM Ingredients
    WHERE ingredient_id = NEW.ingredient_id_2;
      
    IF is_compound_ing_1 OR is_compound_ing_2 THEN
      SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Only atomic ingredients allowed for "Do not combine"';
    END IF;
END//

DELIMITER ;
