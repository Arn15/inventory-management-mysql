from itertools import product
import json
from service import ManufacturerService
from service import ProductService
from service import IngredientService
from service import CategoryService
from service import ProductBatchService
from service import ManufacturerProductService
from service import IngredientBatchService
from model.Manufacturer import Manufacturer
from model.Category import Category
from model.Product import Product
from model.Ingredient import Ingredient
from utils import Screens

class ManufacturerView:
    def run(self, conn, user_id):
        print("Manufacturer View Running")
        manufacturer = ManufacturerService.get_manufacturer_by_user_id(conn, user_id)
        logged_in = True
        while logged_in:
            Screens.clear_terminal()
            print("\nManufacturer Menu:")
            print("1. Define new Product")
            print("2. Update Product BOM (Recipe)")
            print("3. Create Product Batch")
            print("4. Reports: On hand | Nearly out of stock | Almost expired") # get_prod_on_hand, Get_nearly_out_of_stock, almost_expired_ing
            print("5. Recall/Traceability") # TraceRecall
            print("6. Logout")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.define_product(conn, manufacturer)
            elif choice == '2':
                self.update_product(conn, manufacturer)
            elif choice == '3':
                self.create_product_batch(conn, manufacturer)
            elif choice == '4':
                self.get_report(conn, manufacturer)
            elif choice == '5':
                self.trace_recall(conn, manufacturer)
            elif choice == '6':
                print("Logging out...")
                logged_in = False
            else:
                print("Invalid choice. Please try again.")


    def define_product(self, conn, manufacturer: Manufacturer):
        Screens.clear_terminal()
        print("Define Product Menu:")
        print("Defining a new product...")
        print("Select category for the new product:")
        categories = CategoryService.get_all_categories(conn)
        for i in range(len(categories)):
            print(f"{i+1} {categories[i].display()}")
        category_id = categories[int(input("Enter category: ")) - 1].category_id
        product_name = input("Enter product name: ")
        standard_size = input("Enter standard batch size: ")
        print("Enter the ingredients and quantities")
        recipe_json = self.select_ingredients(conn)
        ProductService.create_product(
            conn,
            manufacturer.manufacturer_id,
            category_id,
            product_name,
            standard_size,
            recipe_json
        )
        input("\nPress any key to go to main menu: ")


    def update_product(self, conn, manufacturer: Manufacturer):
        Screens.clear_terminal()
        print("Update Product Menu:")
        products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer.manufacturer_id)
        for i in range(len(products)):
            print(f"{i+1}. {products[i].display()}")
        product_index = int(input("Select a product to update: ")) - 1
        if 0 <= product_index < len(products):
            product = products[product_index]
            print(f"Selected product: {product.display()}")
            standard_size = input("Enter standard batch size:")
            print("Enter the ingredients and quantities")
            recipe_json = self.select_ingredients(conn)
            isUpdated = ProductService.update_product(conn, manufacturer.manufacturer_id, product.product_id, standard_size, recipe_json)
            if isUpdated:
                print("Product updated successfully.")
            else:
                print("Failed to update product.")
        else:
            print("Invalid product selection.")
        input("\nPress any key to go to main menu: ")


    def create_product_batch(self, conn, manufacturer: Manufacturer):
        Screens.clear_terminal()
        print("Create Product Batch Menu: ")
        manufacturer_products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer.manufacturer_id)
        for i in range(len(manufacturer_products)):
            print(f"{i+1}. {manufacturer_products[i].display()}")
        product_index = int(input("Select a product to update: ")) - 1
        if 0 <= product_index < len(manufacturer_products):
            manufacturer_product = manufacturer_products[product_index]
            print(f"Selected product: {manufacturer_product.display()}")
        else:
            print("Invalid product selection.")
            input("\nPress any key to go to main menu: ")
            return
        batch_quantity = input("Enter batch quantity: ")
        is_batch_created = ProductBatchService.create_product_batch(
                                                                    conn,
                                                                    manufacturer.manufacturer_id,
                                                                    manufacturer_product.product_id,
                                                                    manufacturer_product.version,
                                                                    batch_quantity
                                                                )
        if is_batch_created:
            print(f"Product batch created successfully")
        else:
            print("Failed to create product batch.")
        input("\nPress any key to go to main menu: ")

    
    def get_report(self, conn, manufacturer: Manufacturer):
        Screens.clear_terminal()
        print("Report Menu:")
        print("1. On-hand")
        print("2. Nearly out of stock")
        print("3. Almost expired")
        report = int(input("Select type of report: "))
        if report == 1 or report == 2:
            print("Selected Report For On-hand Products")
            products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer.manufacturer_id)
            for i in range(len(products)):
                print(f"{i+1}. {products[i].display()}")
            product_index = int(input("Select a product to Check: ")) - 1
            if 0 <= product_index < len(products):
                product = products[product_index]
                print(f"Selected product: {product.display()}")
        if report == 1:
            on_hand_report = ManufacturerProductService.get_on_hand_report_of_product(conn, manufacturer.manufacturer_id, product.product_id)
            if on_hand_report is None:
                print("No report against the selected product available")
            else:
                content = [[item[h] for h in list(on_hand_report[0].keys())] for item in on_hand_report]
                Screens.print_table(list(on_hand_report[0].keys()), content)
                # on_hand_report.display()
        elif report == 2:
            print("Selected Report For Nearly Out of Stock Products")
            low_stock_report = ManufacturerProductService.check_low_stock(conn, product.manufacturer_product_id)
            if low_stock_report == []:
                print("All ingredient batches can be used to create one batch of standard size for this Product")
                return
            content = [[item[h] for h in list(low_stock_report[0].keys())] for item in low_stock_report]
            Screens.print_table(list(low_stock_report[0].keys()), content)
            # for ingredient in low_stock_report:
            #     print(ingredient.display)
        elif report == 3:
            print("Selected Report For Almost Expired Products")
            no_of_days = int(input("Enter the no of days to chack the expiry: "))
            expiring_ingrdients = ManufacturerProductService.check_expiring_ingredients(conn, no_of_days)
            if expiring_ingrdients == []:
                print("No ingredient batch expires this quickly!")
                return
            content = [t.get_content() for t in expiring_ingrdients]
            Screens.print_table(expiring_ingrdients[0].get_header(), content)
            # for ingredients in expiring_ingrdients:
            #     ingredients.display()
        else:
            print("Invalid report selection.")
        input("\nPress any key to go to main menu: ")


    def trace_recall(self, conn, manufacturer: Manufacturer):
        Screens.clear_terminal()
        print("Recall/Traceability Menu:")
        Screens.new_line()
        ingredients = IngredientService.get_all_ingredient_lots(conn)
        for i in range(len(ingredients)):
            print(f"{i+1}. ", end="")
            self.display_ingredient(ingredients[i])
        index = int(input("Select the ingredient lot for tracing: ")) - 1
        if index < 0 or index >= len(ingredients):
            print("Invalid selection")
            input("\nPress any key to go to main menu: ")
            return
        ingredient_lot_number = ingredients[index]['ingredient_lot_number']
        trace_recalls = ProductService.trace_product_recall(conn, ingredient_lot_number)
        if trace_recalls == []:
            print("No trace recalls available")
        else:
            content = [t.get_content() for t in trace_recalls]
            Screens.print_table(trace_recalls[0].get_header(), content)
        input("\nPress any key to go to main menu: ")

    def select_ingredients(self, conn):
        # Step 1: Fetch and display all ingredients
        ingredients = IngredientService.get_all_ingredients(conn)
        if ingredients is None:
            print("No ingredients available at the moment")
            input("\nPress any key to go to main menu: ")
            return
        print("\n=== Available Ingredients ===")
        for ingredient in ingredients:
            ingredient.display()

        # Step 2: Collect ingredient ID + quantity from user
        print("\nEnter ingredient ID and quantity (e.g. 1 10)")
        print("Type 'done' when finished.\n")

        selections = []
        while True:
            user_input = input("Ingredient ID and quantity: ").strip()
            if user_input.lower() == "done":
                break
            try:
                ing_id, qty = user_input.split()
                ing_id = int(ing_id)
                qty = float(qty)
                selections.append({
                    "id": ing_id,
                    "qty": qty
                })
            except ValueError:
                print("Invalid input. Format should be: <id> <quantity>")

        # Step 3: Convert to JSON
        selections_json = json.dumps(selections, indent=4)
        print("\nIngredients JSON:")
        print(selections_json)

        # Optional: return JSON for later use
        return selections_json
    
    def display_ingredient(self, ingredient):
        print(
            f"Ingredient Lot Number: {ingredient['ingredient_lot_number']}, "
            f"Ingredient Name: {ingredient['ingredient_name']}, "
            f"Supplier Name: {ingredient['supplier_name']}"
        )