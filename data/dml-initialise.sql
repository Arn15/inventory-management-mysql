DELETE FROM Category;
DELETE FROM Products;
DELETE FROM Manufacturer;
DELETE FROM Manufacturer_Product;
DELETE FROM Supplier;
DELETE FROM Ingredients;
DELETE FROM Supplier_Ingredient;
DELETE FROM Ingredient_Formulation;
DELETE FROM Ingredient_Inventory;
DELETE FROM Product_Inventory;
DELETE FROM Product_Ingredient_Batch_Mapping;
DELETE FROM Recipe;
DELETE FROM Do_Not_Combine;
DELETE FROM User;

INSERT INTO Category VALUES
(2, 'Dinners'),
(3, 'Sides');

INSERT INTO Products VALUES
(100, 'Steak Dinner', 2),
(101, 'Mac & Cheese', 3);

INSERT INTO User VALUES
('MFG001', 'John', 'Smith', 'MANUFACTURER'),
('MFG002', 'Alice', 'Lee', 'MANUFACTURER'),
('SUP020', 'Jane', 'Doe', 'SUPPLIER'),
('SUP021', 'James', 'Miller', 'SUPPLIER'),
('VIEW001', 'Bob', 'Johnson', 'VIEWER');

INSERT INTO Manufacturer VALUES
(101, 'John Smith', 'MFG001'),
(102, 'Alice Lee', 'MFG002');

INSERT INTO Manufacturer_Product VALUES
(100, 101, 100, 1, 100),
(101, 102, 101, 1, 300);

INSERT INTO Supplier VALUES
(20, 'Jane Doe', 'SUP020'),
(21, 'James Miller', 'SUP021');

INSERT INTO Ingredients VALUES
(101, 'Salt', FALSE),
(102, 'Pepper', FALSE),
(104, 'Sodium Phosphate', FALSE),
(106, 'Beef Steak', FALSE),
(108, 'Pasta', FALSE),
(201, 'Seasoning Blend', TRUE),
(301, 'Super Seasoning', TRUE);

CALL AddSupplierIngredientVersion(20, 201, '2025-06-30', 20.0, 8.0);

INSERT INTO Supplier_Ingredient VALUES
(2, 20, 101, 1, NULL, NULL, NULL, NULL),
(3, 21, 101, 1, NULL, NULL, NULL, NULL),
(4, 20, 102, 1, NULL, NULL, NULL, NULL),
(5, 20, 106, 1, NULL, NULL, NULL, NULL),
(6, 20, 108, 1, NULL, NULL, NULL, NULL);

INSERT INTO Ingredient_Formulation VALUES
(1, 101, 6),
(1, 102, 2);

INSERT INTO Ingredient_Inventory (
    ingredient_lot_number,
    supplier_ingredient_id,
    unit_price,
    pack_size,
    remaining_amt,
    expiration_date,
    creation_date,
    ingredient_batch_id
)
VALUES
('I101-S20-B1',2, 0.1, 1000, 1000, '2026-11-15', CURRENT_DATE(),1),
('I101-S21-B1',3, 0.08, 800, 800, '2026-10-30', CURRENT_DATE(),1),
('I101-S20-B2',2, 0.1, 500, 500, '2026-11-01', CURRENT_DATE(),2),
('I101-S20-B3',2, 0.1, 500, 485, '2026-12-15', CURRENT_DATE(),3),
('I102-S20-B1',4, 0.3, 1200, 600, '2026-12-15', CURRENT_DATE(),1),
('I106-S20-B1',5, 0.5, 3000, 3000, '2026-12-15', CURRENT_DATE(),1),
('I106-S20-B2',5, 0.5, 600, 0, '2026-12-20', CURRENT_DATE(),2),
('I108-S20-B1',6, 0.25, 1000, 1000, '2026-09-28', CURRENT_DATE(),1),
('I108-S20-B2',6, 0.25, 6300, 4200, '2026-12-31', CURRENT_DATE(),2),
('I201-S20-B1',1, 2.5, 100, 100, '2026-11-30', CURRENT_DATE(),1),
('I201-S20-B2',1, 2.5, 20, 0, '2026-12-30', CURRENT_DATE(),2);

INSERT INTO Product_Inventory(
    product_lot_number,
    manufacturer_product_id,
    expiration_date,
    quantity,
    product_batch_id
)
VALUES
('P100-M101-B1', 100, '2025-11-15', 100, 1),
('P101-M102-B1', 101, '2025-10-30', 300, 1);

INSERT INTO Product_Ingredient_Batch_Mapping VALUES
('P100-M101-B1', 'I106-S20-B2'),
('P100-M101-B1', 'I201-S20-B2'),
('P101-M102-B1', 'I108-S20-B2'),
('P101-M102-B1', 'I101-S20-B3'),
('P101-M102-B1', 'I102-S20-B1');

INSERT INTO Recipe VALUES
(101, 106, 100, 6.00),
(102, 201, 100, 0.20),
(103, 108, 101, 7.00),
(104, 101, 101, 0.05),
(105, 102, 101, 2.00);
 
INSERT INTO Do_Not_Combine VALUES
(106, 104);
