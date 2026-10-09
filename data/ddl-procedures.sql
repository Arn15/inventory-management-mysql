DELIMITER $$

USE `InventoryManagement` $$

DROP procedure IF EXISTS `InsertCategories` $$

DROP procedure IF EXISTS `InsertSupplier` $$

DROP procedure IF EXISTS `InsertManufacturer` $$

DROP procedure IF EXISTS `CreateSupplierIngredient` $$

DROP procedure IF EXISTS `UpdateSupplierIngredient` $$ ## not being used

DROP procedure IF EXISTS `ViewSupplierIngredients` $$

DROP procedure IF EXISTS `AddSupplierIngredientsAtomic` $$

DROP procedure IF EXISTS `AddSupplierIngredientsCompound` $$

DROP procedure IF EXISTS `CreateIngredientBatch` $$

DROP procedure IF EXISTS `AddDoNotCombineIngredients` $$

DROP procedure IF EXISTS `findBestIngredientLot` $$

DROP procedure IF EXISTS `UpdateProduct` $$

DROP procedure IF EXISTS `computeProductLotNumber` $$

DROP procedure IF EXISTS `CreateProductBatch` $$

DROP procedure IF EXISTS `validate_ingredients_list` $$

DROP procedure IF EXISTS `warn_do_not_combine_in_product_lot` $$

DROP procedure IF EXISTS `get_prod_on_hand` $$

DROP procedure IF EXISTS `get_nearly_out_of_stock` $$

DROP procedure IF EXISTS `almost_expired_ing` $$

DROP procedure IF EXISTS `calc_batch_cost` $$

DROP procedure IF EXISTS `CreateProduct` $$

DROP procedure IF EXISTS `GetManufacturersNotSuppliedBySupplier` $$

DROP procedure IF EXISTS `GetConflictingIngredientsForProductLot` $$

DROP procedure IF EXISTS `GetSupplierSpendByManufacturer` $$

DROP procedure IF EXISTS `TraceRecall` $$

DROP procedure IF EXISTS `EvaluateHealthRisk` $$

DROP procedure IF EXISTS `get_ing_and_lot_no` $$

DROP PROCEDURE IF EXISTS `calc_product_batch_unit_cost` $$

DROP PROCEDURE IF EXISTS `BrowseProductTypes` $$

DROP PROCEDURE IF EXISTS `GenerateIngredientList` $$

DROP PROCEDURE IF EXISTS `CompareProductIncompatibilities` $$

DROP PROCEDURE IF EXISTS `AddSupplierIngredientVersion` $$

DROP PROCEDURE IF EXISTS `InsertIngredient` $$


CREATE PROCEDURE InsertCategories (IN cat_name VARCHAR(255))
BEGIN
    INSERT INTO Category (category_name) VALUES (cat_name);
END$$

CREATE PROCEDURE InsertSupplier (IN sup_name VARCHAR(255))
BEGIN
    INSERT INTO Supplier (supplier_name) VALUES (sup_name);
END$$

CREATE PROCEDURE InsertManufacturer(IN man_name VARCHAR(255))
BEGIN
    INSERT INTO Manufacturer (manufacturer_name) VALUES (man_name);
END$$

CREATE PROCEDURE AddSupplierIngredientsAtomic(IN cur_supplier_id INT, IN ing_id INT)
BEGIN
    INSERT INTO Supplier_Ingredient (supplier_id, ingredient_id, version)
    VALUES (cur_supplier_id, ing_id, 1);
END$$

CREATE PROCEDURE AddSupplierIngredientsCompound(
    IN cur_supplier_id INT,
    IN ing_id INT,
    IN price_per_pack DECIMAL(10,2),
    IN pack_size INT
)
BEGIN
    INSERT INTO Supplier_Ingredient 
    (supplier_id, ingredient_id, version, creation_date, expiration_date, price_per_pack, pack_size)
    VALUES (cur_supplier_id, ing_id, 1, current_date, NULL, price_per_pack, pack_size);
END$$

CREATE PROCEDURE CreateSupplierIngredient(
    IN cur_supplier_id INT,
    IN ing_id INT,
    IN ing_is_compound BOOLEAN,
    IN ing_material_list JSON,
    IN price_per_pack DECIMAL(10,2),
    IN pack_size INT
)
BEGIN
    DECLARE sup_ing_id INT;
    DECLARE valid_ing BOOLEAN;
    DECLARE n INT;
    DECLARE i INT DEFAULT 0;

    DECLARE err_msg TEXT DEFAULT 'Unknown error';

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET err_msg = CONCAT('Ingredient creation failed: ', err_msg);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;

    START TRANSACTION;

    -- Insert depending on atomic or compound
    IF NOT ing_is_compound THEN
        CALL AddSupplierIngredientsAtomic(cur_supplier_id, ing_id);

    ELSE
        CALL AddSupplierIngredientsCompound(
            cur_supplier_id,
            ing_id,
            price_per_pack,
            pack_size
        );

    END IF;

    -- Retrieve the generated supplier_ingredient_id
    SET sup_ing_id = LAST_INSERT_ID();

    -- If compound, insert the formulation
    IF ing_is_compound THEN

        CALL validate_ingredients_list(ing_material_list, valid_ing);
        IF NOT valid_ing THEN
            SET err_msg = 'Some ingredients in formulation cannot be combined';
            SIGNAL SQLSTATE '45000';
        END IF;

        SET n = JSON_LENGTH(ing_material_list);

        WHILE i < n DO
            INSERT INTO Ingredient_Formulation(supplier_ingredient_id, ingredient_id, quantity)
            VALUES (
                sup_ing_id,
                JSON_UNQUOTE(JSON_EXTRACT(ing_material_list, CONCAT('$[', i, '].id'))),
                JSON_UNQUOTE(JSON_EXTRACT(ing_material_list, CONCAT('$[', i, '].qty')))
            );
            SET i = i + 1;
        END WHILE;

    END IF;

    COMMIT;
END$$

CREATE PROCEDURE UpdateSupplierIngredient(
    IN cur_supplier_id INT,
    IN cur_ing_id VARCHAR(100),
    IN new_ing_material_list JSON,
    IN ing_is_compound BOOLEAN,
    IN price_per_pack DECIMAL(10,2),
    IN pack_size INT
)
BEGIN

    DECLARE version_count INT DEFAULT 0;
    DECLARE sup_ing_id INT;
    DECLARE n INT;
    DECLARE i INT DEFAULT 0;
    DECLARE valid_ing BOOLEAN;

    DECLARE err_msg TEXT DEFAULT 'Unknown error';

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET err_msg = CONCAT('Ingredient update operation failed: ', err_msg);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;


    -- Validate formulation only if this is a compound update
    IF ing_is_compound THEN
        CALL validate_ingredients_list(new_ing_material_list, valid_ing);

        IF NOT valid_ing THEN
            SET err_msg = 'Some ingredients in formulation cannot be combined';
            SIGNAL SQLSTATE '45000';
        END IF;
    END IF;


    -- Check if ingredient exists for this supplier (versioning logic)
    SELECT COUNT(*) INTO version_count 
    FROM Supplier_Ingredient
    WHERE supplier_id = cur_supplier_id AND ingredient_id = cur_ing_id;

    IF version_count = 0 THEN
        SET err_msg = 'Cannot update! Ingredient does not exist for this supplier';
        SIGNAL SQLSTATE '45000';
    END IF;


    START TRANSACTION;


    -- Insert new version of supplier_ingredient depending on atomic/compound
    IF NOT ing_is_compound THEN
        
        CALL AddSupplierIngredientsAtomic(cur_supplier_id, cur_ing_id);

    ELSE
        
        CALL AddSupplierIngredientsCompound(
            cur_supplier_id,
            cur_ing_id,
            price_per_pack,
            pack_size
        );

    END IF;


    SET sup_ing_id = LAST_INSERT_ID();


    -- Insert formulation only for compound
    IF ing_is_compound THEN
        
        SET n = JSON_LENGTH(new_ing_material_list);

        WHILE i < n DO
            INSERT INTO Ingredient_Formulation(supplier_ingredient_id, ingredient_id, quantity)
            VALUES (
                sup_ing_id,
                JSON_UNQUOTE(JSON_EXTRACT(new_ing_material_list, CONCAT('$[', i, '].id'))),
                JSON_UNQUOTE(JSON_EXTRACT(new_ing_material_list, CONCAT('$[', i, '].qty')))
            );

            SET i = i + 1;
        END WHILE;

    END IF;


    COMMIT;
END$$


CREATE PROCEDURE ViewSupplierIngredients(IN cur_supplier_id INT)
BEGIN
    SELECT i.name, si.supplier_ingredient_id, si.supplier_id, i.ingredient_id, si.version
    FROM Supplier_Ingredient si JOIN Ingredients i ON si.ingredient_id = i.ingredient_id 
    WHERE si.supplier_id = cur_supplier_id;
END$$

CREATE PROCEDURE CreateIngredientBatch(
    IN cur_supplier_id INT,
    IN ing_id INT,
    IN batch_unit_price DECIMAL(10,2),
    IN batch_pack_size INT,
    IN batch_exp_date DATE
)
BEGIN

    DECLARE supplier_ing_id INT;
  
    DECLARE err_msg TEXT DEFAULT 'Unknown error';
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN     
      ROLLBACK;
  
      SET err_msg = CONCAT('Ingredient batch creation failed: ', err_msg);
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;

    SELECT supplier_ingredient_id into supplier_ing_id
    FROM Supplier_Ingredient
    WHERE supplier_id = cur_supplier_id AND ingredient_id = ing_id
    ORDER BY version DESC 
    LIMIT 1;

    IF supplier_ing_id IS NULL THEN
        SET err_msg = 'Current supplier does not supply this ingredient';
        SIGNAL SQLSTATE '45000'; 
    ELSE      
        START TRANSACTION;
    
        INSERT INTO Ingredient_Inventory (supplier_ingredient_id, unit_price, pack_size, remaining_amt, expiration_date)
        VALUES (supplier_ing_id, batch_unit_price, batch_pack_size, batch_pack_size, batch_exp_date);
    
        COMMIT;
    END IF;
END$$

CREATE PROCEDURE AddDoNotCombineIngredients(
  IN ing_id_1 INT,
  IN ing_id_2 INT
)
BEGIN
    DECLARE err_msg TEXT DEFAULT 'Unknown error';
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN     
      ROLLBACK;
  
      SET err_msg = CONCAT('Operation failed: ', err_msg);
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;

  START TRANSACTION;

  INSERT INTO Do_Not_Combine(ingredient_id_1, ingredient_id_2)
  VALUES (ing_id_1, ing_id_2);

  COMMIT;
END$$

CREATE PROCEDURE CreateProduct(
    IN cur_manufacturer_id INT,
    IN product_cat_id INT,
    IN new_product_name VARCHAR(255),
    IN standard_batch_size INT,
    IN recipe_ing_list JSON
)
BEGIN

    DECLARE new_product_id INT;
    DECLARE new_manufacturer_prod_id INT;
    DECLARE n INT;
    DECLARE i INT DEFAULT 0;
    DECLARE valid_ing BOOLEAN;

    DECLARE err_msg TEXT DEFAULT 'Unknown error';
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN     
      ROLLBACK;
  
      SET err_msg = CONCAT('Product creation failed: ', err_msg);
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;


    CALL validate_ingredients_list(recipe_ing_list, valid_ing);
    IF NOT valid_ing THEN
        SET err_msg = 'Some ingredients in recipe cannot be combined';
        SIGNAL SQLSTATE '45000';
    END IF;


    START TRANSACTION;

    INSERT INTO Products(cat_id, product_name)
    VALUES (product_cat_id, new_product_name);

    SET new_product_id = LAST_INSERT_ID();

    INSERT INTO Manufacturer_Product(manufacturer_id, product_id, standard_size)
    VALUES (cur_manufacturer_id, new_product_id, standard_batch_size);

    SET new_manufacturer_prod_id = LAST_INSERT_ID();    

    SET n = JSON_LENGTH(recipe_ing_list);
    WHILE i < n DO
        INSERT INTO Recipe(manufacturer_product_id, ingredient_id, quantity)
        VALUES (
            new_manufacturer_prod_id,
            JSON_UNQUOTE(JSON_EXTRACT(recipe_ing_list, CONCAT('$[', i, '].id'))),
            JSON_UNQUOTE(JSON_EXTRACT(recipe_ing_list, CONCAT('$[', i, '].qty')))
        );
        SET i = i + 1;
    END WHILE;

    COMMIT;
END$$

CREATE PROCEDURE UpdateProduct(
    IN cur_manufacturer_id INT,
    IN cur_prod_id INT,
    IN standard_batch_size INT,
    IN new_recipe_ing_list JSON
)
BEGIN

    DECLARE new_manufacturer_prod_id INT;
    DECLARE version_count INT DEFAULT 0;
    DECLARE n INT;
    DECLARE i INT DEFAULT 0;
    DECLARE valid_ing BOOLEAN;
    
    DECLARE err_msg TEXT DEFAULT 'Unknown error';
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN     
      ROLLBACK;
  
      SET err_msg = CONCAT('Product update failed: ', err_msg);
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;

    SELECT COUNT(*) INTO version_count
    FROM Manufacturer_Product
    WHERE manufacturer_id = cur_manufacturer_id AND product_id = cur_prod_id;

    IF version_count = 0 THEN
        SET err_msg = 'Cannot perform update operation! Product does not exist or is not manufactured by current manufacturer';
        SIGNAL SQLSTATE '45000';
    END IF;


    CALL validate_ingredients_list(new_recipe_ing_list, valid_ing);
    IF NOT valid_ing THEN
        SET err_msg = 'Some ingredients in recipe cannot be combined';
        SIGNAL SQLSTATE '45000';
    END IF;


    START TRANSACTION;

    INSERT INTO Manufacturer_Product(manufacturer_id, product_id, standard_size)
    VALUES (cur_manufacturer_id, cur_prod_id, standard_batch_size);
    SET new_manufacturer_prod_id = LAST_INSERT_ID();

    SET n = JSON_LENGTH(new_recipe_ing_list);
    WHILE i < n DO
        INSERT INTO Recipe(manufacturer_product_id, ingredient_id, quantity)
        VALUES (
            new_manufacturer_prod_id,
            JSON_UNQUOTE(JSON_EXTRACT(new_recipe_ing_list, CONCAT('$[', i, '].id'))),
            JSON_UNQUOTE(JSON_EXTRACT(new_recipe_ing_list, CONCAT('$[', i, '].qty')))
        );
        SET i = i + 1;
    END WHILE;

    COMMIT;
END$$

CREATE PROCEDURE findBestIngredientLot(
  IN ing_id INT,
  IN ing_qty INT,
  OUT ing_lot_number VARCHAR(255)
)
BEGIN
  
  SELECT iv.ingredient_lot_number INTO ing_lot_number
  FROM Ingredient_Inventory iv
  JOIN Supplier_Ingredient si on si.supplier_ingredient_id = iv.supplier_ingredient_id
  WHERE si.ingredient_id = ing_id AND iv.remaining_amt >= ing_qty
  ORDER BY iv.expiration_date DESC, iv.creation_date ASC
  LIMIT 1;
  
END$$

CREATE PROCEDURE computeProductLotNumber(
  IN manu_prod_id INT,
  OUT prod_lot_num VARCHAR(255)
)
BEGIN 
  DECLARE manu_id INT;
  DECLARE prod_id INT;
  DECLARE batch_count INT DEFAULT 0;

  SELECT manufacturer_id, product_id INTO manu_id, prod_id
  FROM Manufacturer_Product
  WHERE manufacturer_product_id = manu_prod_id;

  SELECT COUNT(*) INTO batch_count
  FROM Product_Inventory
  WHERE manufacturer_product_id = manu_prod_id;

  SELECT CONCAT('P', prod_id, '-', 'M', manu_id, '-', 'B', (batch_count + 1)) INTO prod_lot_num;
    
END$$


CREATE PROCEDURE CreateProductBatch(
    IN cur_manufacturer_id INT,
    IN cur_prod_id INT,
    IN recipe_version INT,
    IN batch_quantity INT
)
BEGIN

    DECLARE cur_manufacturer_prod_id INT;
    DECLARE end_of_recipe BOOLEAN DEFAULT FALSE;
    DECLARE cur_ing_id INT;
    DECLARE cur_ing_qty DECIMAL(10, 2);
    DECLARE cur_ing_lot_num VARCHAR(255);
    DECLARE new_prod_lot_num VARCHAR(255);
    DECLARE prod_expiration_date DATE DEFAULT CURRENT_DATE();
    DECLARE cur_ing_exp_date DATE;
    DECLARE err_msg TEXT DEFAULT 'Unknown error';

    DECLARE recipe_cursor CURSOR FOR
        SELECT ingredient_id, quantity
        FROM Recipe
        WHERE manufacturer_product_id = cur_manufacturer_prod_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET end_of_recipe = TRUE;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET err_msg = CONCAT('Product batch creation failed: ', err_msg);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END;

    SELECT manufacturer_product_id INTO cur_manufacturer_prod_id
    FROM Manufacturer_Product
    WHERE manufacturer_id = cur_manufacturer_id
      AND product_id = cur_prod_id
      AND version = recipe_version;

    IF cur_manufacturer_prod_id IS NULL THEN
        SET err_msg = 'Unable to find such a version of product manufactured by the current manufacturer';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
    END IF;

    START TRANSACTION;

        CALL computeProductLotNumber(cur_manufacturer_prod_id, new_prod_lot_num);

        INSERT INTO Product_Inventory(manufacturer_product_id, expiration_date, quantity)
        VALUES (cur_manufacturer_prod_id, CURRENT_DATE(), batch_quantity);

        OPEN recipe_cursor;
        FETCH FROM recipe_cursor INTO cur_ing_id, cur_ing_qty;

        WHILE NOT end_of_recipe DO
            CALL findBestIngredientLot(cur_ing_id, cur_ing_qty * batch_quantity, cur_ing_lot_num);

            IF cur_ing_lot_num IS NULL THEN
                SET err_msg = 'Required ingredients not available to produce the batch';
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = err_msg;
            END IF;

            INSERT INTO Product_Ingredient_Batch_Mapping(product_lot_number, ingredient_lot_number)
            VALUES (new_prod_lot_num, cur_ing_lot_num);

            SELECT expiration_date INTO cur_ing_exp_date
            FROM Ingredient_Inventory
            WHERE ingredient_lot_number = cur_ing_lot_num;

            SET prod_expiration_date = LEAST(prod_expiration_date, cur_ing_exp_date);

            UPDATE Ingredient_Inventory
            SET remaining_amt = remaining_amt - cur_ing_qty
            WHERE ingredient_lot_number = cur_ing_lot_num;

            FETCH FROM recipe_cursor INTO cur_ing_id, cur_ing_qty;
        END WHILE;

        CLOSE recipe_cursor;

        UPDATE Product_Inventory
        SET expiration_date = prod_expiration_date
        WHERE product_lot_number = new_prod_lot_num;

    COMMIT;

    CALL warn_do_not_combine_in_product_lot(new_prod_lot_num);

END$$

CREATE PROCEDURE validate_ingredients_list(
    IN ing_list JSON,
    OUT valid BOOLEAN
)
BEGIN
    WITH input_ingredients AS (
        SELECT JSON_UNQUOTE(JSON_EXTRACT(t.obj, '$.id')) AS ing_id
        FROM JSON_TABLE(
            ing_list,
            '$[*]' COLUMNS (obj JSON PATH '$')
        ) AS t
    ),
    invalid_pairs AS (
        SELECT a.ing_id AS ing1, b.ing_id AS ing2
        FROM input_ingredients a
        JOIN input_ingredients b ON a.ing_id < b.ing_id
        JOIN Do_Not_Combine dnc
          ON (
              (dnc.ingredient_id_1 = a.ing_id AND dnc.ingredient_id_2 = b.ing_id)
           OR (dnc.ingredient_id_1 = b.ing_id AND dnc.ingredient_id_2 = a.ing_id)
          )
    )
    SELECT NOT EXISTS (SELECT 1 FROM invalid_pairs) INTO valid;
END$$

CREATE PROCEDURE warn_do_not_combine_in_product_lot(
  IN prod_lot_num VARCHAR(255)
)
BEGIN

  DECLARE valid BOOLEAN;

  WITH batch_ingredients AS (
    SELECT si.supplier_ingredient_id, si.ingredient_id
    FROM Product_Ingredient_Batch_Mapping pm
    JOIN Ingredient_Inventory iv ON pm.ingredient_lot_number = iv.ingredient_lot_number
    JOIN Supplier_Ingredient si ON iv.supplier_ingredient_id = si.supplier_ingredient_id
    WHERE pm.product_lot_number = prod_lot_num
  ),
  all_atomic_ingredients AS (
    SELECT bi.ingredient_id
    FROM batch_ingredients bi

    UNION ALL

    SELECT inf.ingredient_id
    FROM Ingredient_Formulation inf
    JOIN Supplier_Ingredient si ON inf.supplier_ingredient_id = si.supplier_ingredient_id
    JOIN batch_ingredients bi ON bi.ingredient_id = si.ingredient_id
  ),
  atomic_ingredients AS (
    SELECT DISTINCT(ingredient_id) FROM all_atomic_ingredients
  ),
  invalid_pairs AS (
    SELECT a.ingredient_id AS ing1, b.ingredient_id AS ing2
    FROM atomic_ingredients a
    JOIN atomic_ingredients b ON a.ingredient_id < b.ingredient_id
    JOIN Do_Not_Combine dnc
      ON (
          (dnc.ingredient_id_1 = a.ingredient_id AND dnc.ingredient_id_2 = b.ingredient_id)
       OR (dnc.ingredient_id_1 = b.ingredient_id AND dnc.ingredient_id_2 = a.ingredient_id)
      )
  )
  SELECT NOT EXISTS (SELECT 1 FROM invalid_pairs) INTO valid;

  IF NOT valid THEN
    SELECT '"Do Not Combine" ingredient-pair(s) are present in the created product lot' as WARNING;
  END IF;  
  
END$$

CREATE PROCEDURE get_prod_on_hand(
  IN cur_manu_id INT,
  IN cur_prod_id INT
)
BEGIN 

  SELECT mp.version, pi.product_lot_number, pi.quantity
  FROM Manufacturer_Product mp, Product_Inventory pi
  WHERE mp.manufacturer_product_id = pi.manufacturer_product_id AND mp.manufacturer_id = cur_manu_id and mp.product_id = cur_prod_id
  ORDER BY mp.version;

END$$

CREATE PROCEDURE get_nearly_out_of_stock(
  IN cur_manu_prod_id INT
)
BEGIN 

  DECLARE batch_qty INT;

  SELECT standard_size INTO batch_qty
  FROM Manufacturer_Product mp WHERE mp.manufacturer_product_id = cur_manu_prod_id;

  SELECT i.name, iv.ingredient_lot_number, iv.remaining_amt, (r.quantity * batch_qty) as required_amt
  FROM Recipe r
  JOIN Ingredient_Inventory iv ON iv.ingredient_lot_number LIKE CONCAT('I', r.ingredient_id, '-%')
  JOIN Ingredients i ON r.ingredient_id = i.ingredient_id
  WHERE iv.remaining_amt < (r.quantity * batch_qty);

END$$

CREATE PROCEDURE almost_expired_ing(
  IN days_to_expiry INT
)
BEGIN 
  SELECT *
  FROM Ingredient_Inventory
  WHERE expiration_date < DATE_ADD(CURDATE(), INTERVAL days_to_expiry DAY);

END$$

CREATE PROCEDURE calc_batch_cost(
  IN prod_lot_num VARCHAR(255),
  OUT total_cost DECIMAL(10,2)
)
BEGIN 

  DECLARE cur_manu_prod_id INT;
  DECLARE batch_qty INT;

  SELECT manufacturer_product_id, quantity INTO cur_manu_prod_id, batch_qty
  FROM Product_Inventory 
  WHERE product_lot_number = prod_lot_num;

  WITH ing_lots AS (
    SELECT ingredient_lot_number
    FROM Product_Ingredient_Batch_Mapping
    WHERE product_lot_number = prod_lot_num
  ),
  cost_summary AS (
    SELECT (iv.unit_price * r.quantity * batch_qty) AS cost
    FROM Recipe r
    JOIN Ingredient_Inventory iv 
      ON iv.ingredient_lot_number LIKE CONCAT('I', r.ingredient_id, '-%')
    WHERE r.manufacturer_product_id = cur_manu_prod_id
  )
  SELECT SUM(cost) INTO total_cost
  FROM cost_summary;

END$$



CREATE PROCEDURE GetManufacturersNotSuppliedBySupplier(
    IN cur_supplier_id INT
)
BEGIN
    SELECT m.manufacturer_id, m.manufacturer_name
    FROM Manufacturer m
    WHERE m.manufacturer_id NOT IN (
        SELECT DISTINCT mp.manufacturer_id
        FROM Manufacturer_Product mp
        JOIN Product_Inventory pi 
            ON mp.manufacturer_product_id = pi.manufacturer_product_id
        JOIN Product_Ingredient_Batch_Mapping pibm 
            ON pi.product_lot_number = pibm.product_lot_number
        JOIN Ingredient_Inventory ii 
            ON pibm.ingredient_lot_number = ii.ingredient_lot_number
        JOIN Supplier_Ingredient si 
            ON ii.supplier_ingredient_id = si.supplier_ingredient_id
        WHERE si.supplier_id = cur_supplier_id
    )
    ORDER BY m.manufacturer_name;
END $$

CREATE PROCEDURE GetConflictingIngredientsForProductLot(
    IN cur_product_lot_number VARCHAR(255)
)
BEGIN
    SELECT DISTINCT 
        i_conflict.ingredient_id,
        i_conflict.name AS conflicting_ingredient_name
    FROM Product_Inventory pi
    JOIN Manufacturer_Product mp 
        ON pi.manufacturer_product_id = mp.manufacturer_product_id
    JOIN Recipe r 
        ON r.manufacturer_product_id = mp.manufacturer_product_id
    JOIN Do_Not_Combine dnc 
        ON r.ingredient_id IN (dnc.ingredient_id_1, dnc.ingredient_id_2)
    JOIN Ingredients i_conflict 
        ON i_conflict.ingredient_id = 
            CASE 
                WHEN r.ingredient_id = dnc.ingredient_id_1 THEN dnc.ingredient_id_2
                ELSE dnc.ingredient_id_1
            END
    WHERE pi.product_lot_number = cur_product_lot_number
    ORDER BY i_conflict.name;
END $$

CREATE PROCEDURE GetSupplierSpendByManufacturer(
    IN cur_manufacturer_code VARCHAR(255)
)
BEGIN
    SELECT 
        s.supplier_id,
        s.supplier_name,
        SUM(ii.unit_price * ii.pack_size) AS total_spent
    FROM Manufacturer m
    JOIN Manufacturer_Product mp 
        ON m.manufacturer_id = mp.manufacturer_id
    JOIN Product_Inventory pi 
        ON mp.manufacturer_product_id = pi.manufacturer_product_id
    JOIN Product_Ingredient_Batch_Mapping pibm 
        ON pi.product_lot_number = pibm.product_lot_number
    JOIN Ingredient_Inventory ii 
        ON pibm.ingredient_lot_number = ii.ingredient_lot_number
    JOIN Supplier_Ingredient si 
        ON ii.supplier_ingredient_id = si.supplier_ingredient_id
    JOIN Supplier s 
        ON si.supplier_id = s.supplier_id
    WHERE m.manufacturer_id = cur_manufacturer_code
    GROUP BY s.supplier_id, s.supplier_name
    ORDER BY total_spent DESC;
END $$

CREATE PROCEDURE TraceRecall(
    IN recall_ing_or_lot VARCHAR(255)
)
BEGIN
    SELECT DISTINCT pm.product_lot_number,
                    pi.expiration_date,
                    mp.product_id,
                    p.product_name,
                    m.manufacturer_name
    FROM Product_Ingredient_Batch_Mapping pm
    JOIN Product_Inventory pi ON pm.product_lot_number = pi.product_lot_number
    JOIN Manufacturer_Product mp ON pi.manufacturer_product_id = mp.manufacturer_product_id
    JOIN Products p ON mp.product_id = p.product_id
    JOIN Manufacturer m ON mp.manufacturer_id = m.manufacturer_id
    WHERE pm.ingredient_lot_number = recall_ing_or_lot
    ORDER BY m.manufacturer_name, p.product_name;
END$$



CREATE PROCEDURE EvaluateHealthRisk(
    IN prod_lot_num VARCHAR(255)
)
BEGIN
    DECLARE conflict_count INT DEFAULT 0;

    WITH batch_ingredients AS (
        SELECT si.ingredient_id
        FROM Product_Ingredient_Batch_Mapping pm
        JOIN Ingredient_Inventory iv ON pm.ingredient_lot_number = iv.ingredient_lot_number
        JOIN Supplier_Ingredient si ON iv.supplier_ingredient_id = si.supplier_ingredient_id
        WHERE pm.product_lot_number = prod_lot_num
    ),
    flattened AS (
        SELECT bi.ingredient_id AS atomic_ing_id
        FROM batch_ingredients bi
        UNION
        SELECT inf.ingredient_id
        FROM Ingredient_Formulation inf
        JOIN Supplier_Ingredient si ON inf.supplier_ingredient_id = si.supplier_ingredient_id
        JOIN batch_ingredients bi ON bi.ingredient_id = si.ingredient_id
    ),
    invalid_pairs AS (
        SELECT a.atomic_ing_id AS ing1, b.atomic_ing_id AS ing2
        FROM flattened a
        JOIN flattened b ON a.atomic_ing_id < b.atomic_ing_id
        JOIN Do_Not_Combine dnc
          ON (dnc.ingredient_id_1 = a.atomic_ing_id AND dnc.ingredient_id_2 = b.atomic_ing_id)
          OR (dnc.ingredient_id_2 = a.atomic_ing_id AND dnc.ingredient_id_1 = b.atomic_ing_id)
    )
    SELECT COUNT(*) INTO conflict_count FROM invalid_pairs;

    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Health Risk Detected — Do-Not-Combine ingredient pair(s) found in batch!';
    END IF;
END$$

-- List the ingredients and the lot number of the last batch of product type Steak Dinner (100) made by manufacturer MFG001.
CREATE PROCEDURE get_ing_and_lot_no(
  IN prod_id INT,
  IN man_id INT
)
BEGIN
  DECLARE v_mp_id INT;
  DECLARE v_lot VARCHAR(255);

  -- Get latest manufacturer_product_id
  SELECT manufacturer_product_id INTO v_mp_id
  FROM Manufacturer_Product
  WHERE product_id = prod_id AND manufacturer_id = man_id
  ORDER BY version DESC
  LIMIT 1;

  IF v_mp_id IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No such product found for this manufacturer';
  END IF;

  -- Get last batch for that manufacturer_product_id
  SELECT product_lot_number INTO v_lot
  FROM Product_Inventory
  WHERE manufacturer_product_id = v_mp_id
  ORDER BY product_batch_id DESC
  LIMIT 1;

  IF v_lot IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No batch found for this product';
  END IF;

  -- Return all ingredients & lot numbers
  SELECT
      iv.ingredient_lot_number,
      i.name AS ingredient_name
  FROM Product_Ingredient_Batch_Mapping pm
  JOIN Ingredient_Inventory iv 
      ON pm.ingredient_lot_number = iv.ingredient_lot_number
  JOIN Supplier_Ingredient si
      ON iv.supplier_ingredient_id = si.supplier_ingredient_id
  JOIN Ingredients i
      ON si.ingredient_id = i.ingredient_id
  WHERE pm.product_lot_number = v_lot;


  -- Return all ingredients & lot numbers
  SELECT
      iv.ingredient_lot_number,
      i.name AS ingredient_name
  FROM Product_Ingredient_Batch_Mapping pm
  JOIN Ingredient_Inventory iv 
      ON pm.ingredient_lot_number = iv.ingredient_lot_number
  JOIN Supplier_Ingredient si
      ON iv.supplier_ingredient_id = si.supplier_ingredient_id
  JOIN Ingredients i
      ON si.ingredient_id = i.ingredient_id
  WHERE pm.product_lot_number = v_lot;

END $$

-- For product with lot number 100-MFG001-B0901, find the unit cost for that product.
CREATE PROCEDURE calc_product_batch_unit_cost(
  IN prod_lot_num VARCHAR(255)
)
BEGIN
  DECLARE batch_quantity INT;
  DECLARE batch_total DECIMAL(10,2);
  CALL calc_batch_cost(prod_lot_num, batch_total);

  SELECT quantity INTO batch_quantity
  FROM Product_Inventory
  WHERE product_lot_number = prod_lot_num
  LIMIT 1;

  -- Return unit cost
  IF batch_quantity > 0 THEN
      SELECT batch_total / batch_quantity AS unit_cost;
  ELSE
      SELECT NULL AS unit_cost;
  END IF;
END $$


CREATE PROCEDURE BrowseProductTypes()
BEGIN
    SELECT 
        c.category_name AS Category,
        m.manufacturer_name AS Manufacturer,
        p.product_name AS Product,
        mp.version AS Version,
        mp.standard_size AS Standard_Size
    FROM Manufacturer_Product mp
    JOIN Manufacturer m ON mp.manufacturer_id = m.manufacturer_id
    JOIN Products p ON mp.product_id = p.product_id
    JOIN Category c ON p.cat_id = c.category_id
    ORDER BY c.category_name, m.manufacturer_name, p.product_name;
END $$

CREATE PROCEDURE GenerateIngredientList(IN in_product_lot_number VARCHAR(255))
BEGIN

    WITH RECURSIVE IngredientTree AS (

        -- BASE: Direct ingredients used by this product lot
        SELECT
            si.ingredient_id,                         -- actual ingredient ID
            ing.name AS ingredient_name,              -- ingredient name
            r.quantity AS qty_from_recipe,            -- correct quantity from recipe
            ii.supplier_ingredient_id,                -- version of ingredient used
            ing.isCompound                            -- compound or raw?
        FROM Product_Ingredient_Batch_Mapping pibm
        JOIN Ingredient_Inventory ii 
            ON pibm.ingredient_lot_number = ii.ingredient_lot_number
        JOIN Supplier_Ingredient si 
            ON ii.supplier_ingredient_id = si.supplier_ingredient_id
        JOIN Ingredients ing 
            ON si.ingredient_id = ing.ingredient_id

        -- join to product table to get manufacturer_product_id
        JOIN Product_Inventory pi
            ON pibm.product_lot_number = pi.product_lot_number

        -- join recipe to get correct quantity
        JOIN Recipe r
            ON r.manufacturer_product_id = pi.manufacturer_product_id
           AND r.ingredient_id = si.ingredient_id

        WHERE pibm.product_lot_number = in_product_lot_number


        UNION ALL

        -- RECURSIVE: expand compound ingredients using actual supplier ingredient version
        SELECT
            f.ingredient_id,
            ing2.name AS ingredient_name,
            it.qty_from_recipe * f.quantity AS qty_from_recipe,
            f.supplier_ingredient_id,
            ing2.isCompound
        FROM Ingredient_Formulation f
        JOIN Ingredients ing2 
            ON f.ingredient_id = ing2.ingredient_id
        JOIN IngredientTree it 
            ON it.supplier_ingredient_id = f.supplier_ingredient_id
        WHERE it.isCompound = TRUE
    )

    -- FINAL OUTPUT: only non-compound (raw) ingredients
    SELECT 
        ingredient_id,
        ingredient_name,
        qty_from_recipe
    FROM IngredientTree
    WHERE isCompound = FALSE;

END $$

CREATE PROCEDURE CompareProductIncompatibilities(
    IN prod_id_1 INT,
    IN prod_id_2 INT
)
BEGIN
    SELECT 
        dnc.ingredient_id_1,
        i1.name AS ingredient_1_name,
        dnc.ingredient_id_2,
        i2.name AS ingredient_2_name
    FROM Do_Not_Combine dnc
    JOIN Ingredients i1 ON dnc.ingredient_id_1 = i1.ingredient_id
    JOIN Ingredients i2 ON dnc.ingredient_id_2 = i2.ingredient_id
    WHERE 
        dnc.ingredient_id_1 IN (
            SELECT ingredient_id FROM Recipe WHERE manufacturer_product_id IN (prod_id_1, prod_id_2)
        )
        AND
        dnc.ingredient_id_2 IN (
            SELECT ingredient_id FROM Recipe WHERE manufacturer_product_id IN (prod_id_1, prod_id_2)
        );
END $$

DELIMITER $$

CREATE PROCEDURE AddSupplierIngredientVersion(
    IN p_supplier_id INT,
    IN p_ingredient_id INT,
    IN p_start_date DATE,
    IN p_price_per_pack DECIMAL(10,2),
    IN p_pack_size DECIMAL(10,2)
)
BEGIN
    DECLARE last_version INT DEFAULT 0;

    -- Find the last version for this supplier+ingredient
    SELECT COALESCE(MAX(version), 0)
    INTO last_version
    FROM Supplier_Ingredient
    WHERE supplier_id = p_supplier_id
      AND ingredient_id = p_ingredient_id;

    -- Expire the previous version, if any
    IF last_version > 0 THEN
        UPDATE Supplier_Ingredient
        SET expiration_date = CURRENT_DATE()
        WHERE supplier_id = p_supplier_id
          AND ingredient_id = p_ingredient_id
          AND version = last_version;
    END IF;

    -- Insert the new version
    INSERT INTO Supplier_Ingredient (
        supplier_id,
        ingredient_id,
        version,
        expiration_date,
        creation_date,
        price_per_pack,
        pack_size
    )
    VALUES (
        p_supplier_id,
        p_ingredient_id,
        last_version + 1,
        NULL,                   -- new version is unexpired
        p_start_date,           -- when this version becomes active
        p_price_per_pack,
        p_pack_size
    );
END $$



DELIMITER $$

CREATE PROCEDURE InsertIngredient(
    IN p_name VARCHAR(255),
    IN p_isCompound BOOLEAN
)
BEGIN
    DECLARE existing_id INT;

    -- Check for existing ingredient (case-insensitive)
    SELECT ingredient_id INTO existing_id
    FROM Ingredients
    WHERE LOWER(name) = LOWER(p_name)
    LIMIT 1;

    IF existing_id IS NOT NULL THEN
        SELECT CONCAT('Ingredient "', p_name, '" already exists with ID = ', existing_id) AS message;
    ELSE
        INSERT INTO Ingredients(name, isCompound)
        VALUES (p_name, p_isCompound);

        SELECT CONCAT('Inserted ingredient with ID = ', LAST_INSERT_ID()) AS message;
    END IF;
END$$


DELIMITER ;
