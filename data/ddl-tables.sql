USE `InventoryManagement`;

DROP TABLE IF EXISTS Ingredient_Formulation;
DROP TABLE IF EXISTS Do_Not_Combine;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS Product_Ingredient_Batch_Mapping;
DROP TABLE IF EXISTS Product_Inventory;
DROP TABLE IF EXISTS Ingredient_Inventory;
DROP TABLE IF EXISTS Supplier_Ingredient;
DROP TABLE IF EXISTS Ingredients;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Manufacturer_Product;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS User;

CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL
);


CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    cat_id INT NOT NULL,
    FOREIGN KEY (cat_id) REFERENCES Category(category_id)
);

CREATE TABLE User
(
	user_id VARCHAR(10) PRIMARY KEY,
	first_name VARCHAR(20),
	last_name VARCHAR(20),
	role_code ENUM('MANUFACTURER', 'SUPPLIER', 'VIEWER')
);

CREATE TABLE Manufacturer (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


CREATE TABLE Manufacturer_Product (
    manufacturer_product_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT NOT NULL,
    product_id INT NOT NULL,
    version INT NOT NULL,
    standard_size INT NOT NULL,
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    UNIQUE (manufacturer_id, product_id, version)
);


CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


CREATE TABLE Ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    isCompound BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE Supplier_Ingredient (
    supplier_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    version INT NOT NULL,
    expiration_date DATE ,
    creation_date DATE DEFAULT (CURRENT_DATE()),
    price_per_pack DECIMAL(10,2),
    pack_size INT,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id),
    UNIQUE (supplier_id, ingredient_id, version)
);


CREATE TABLE Ingredient_Inventory (
    ingredient_lot_number VARCHAR(255) PRIMARY KEY,
    supplier_ingredient_id INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    pack_size INT NOT NULL,
    remaining_amt INT NOT NULL,
    expiration_date DATE NOT NULL,
    creation_date DATE NOT NULL DEFAULT (CURRENT_DATE()),
    ingredient_batch_id INT NOT NULL,
    FOREIGN KEY (supplier_ingredient_id) REFERENCES Supplier_Ingredient(supplier_ingredient_id),
    UNIQUE (supplier_ingredient_id, ingredient_batch_id)
);


CREATE TABLE Product_Inventory (
    product_lot_number VARCHAR(255) PRIMARY KEY,
    manufacturer_product_id INT NOT NULL,
    expiration_date DATE NOT NULL,
    creation_date DATE NOT NULL DEFAULT (CURRENT_DATE()),
    quantity INT NOT NULL,
    product_batch_id INT NOT NULL,
    FOREIGN KEY (manufacturer_product_id) REFERENCES Manufacturer_Product(manufacturer_product_id),
    UNIQUE (manufacturer_product_id, product_batch_id)
);


CREATE TABLE Product_Ingredient_Batch_Mapping (
    product_lot_number VARCHAR(255) NOT NULL,
    ingredient_lot_number VARCHAR(255) NOT NULL,
    PRIMARY KEY (product_lot_number, ingredient_lot_number),
    FOREIGN KEY (product_lot_number) REFERENCES Product_Inventory(product_lot_number),
    FOREIGN KEY (ingredient_lot_number) REFERENCES Ingredient_Inventory(ingredient_lot_number)
);


CREATE TABLE Recipe (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT NOT NULL,
    manufacturer_product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id),
    FOREIGN KEY (manufacturer_product_id) REFERENCES Manufacturer_Product(manufacturer_product_id)
);


CREATE TABLE Do_Not_Combine (
    ingredient_id_1 INT NOT NULL,
    ingredient_id_2 INT NOT NULL,
    PRIMARY KEY (ingredient_id_1, ingredient_id_2),
    FOREIGN KEY (ingredient_id_1) REFERENCES Ingredients(ingredient_id),
    FOREIGN KEY (ingredient_id_2) REFERENCES Ingredients(ingredient_id)
);


CREATE TABLE Ingredient_Formulation (
    supplier_ingredient_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (supplier_ingredient_id, ingredient_id),
    FOREIGN KEY (supplier_ingredient_id) REFERENCES Supplier_Ingredient(supplier_ingredient_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);

