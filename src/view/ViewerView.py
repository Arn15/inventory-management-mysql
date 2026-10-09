from utils import Screens
from service import IngredientService
from service import ProductService
from service import ManufacturerService
from service import ManufacturerProductService
from service import ProductBatchService
from service import SupplierService
from service import SupplierIngredientService
from service import ManufacturerSupplierService

class ViewerView:
    def run(self, conn, user_id):
        print("Viewer View Running")
        logged_in = True
        while logged_in:
            Screens.clear_terminal()
            print("\nViewer Menu:")
            print("1. Browse Product Types")
            print("2. Generate Ingredient List")
            print("3. Compare Two Product Types for Incompatibilities")
            print("4. Get last batch of manufacturer product")
            print("5. Get Supplier Spent for a Manufacturer")
            print("6. Get unit cost of a product using lot number")
            print("7. Get Conflicting Ingredients Using A Product Lot Number")
            print("8. Get Manufacturers Not Supplied By A Supplier")
            print("9. Logout")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.view_products_types(conn)
            elif choice == '2':
                self.generate_ingredient_list(conn)
            elif choice == '3':
                self.get_do_not_combine_pairs(conn)
            elif choice == '4':
                self.get_last_batch_of_manufacturer_product(conn)
            elif choice == '5':
                self.get_supplier_spent_for_manufacturer(conn)
            elif choice == '6':
                self.get_unit_cost_of_product_with_lot_number(conn)
            elif choice == '7':
                self.get_conflicting_ingredients_using_product_lot_number(conn)
            elif choice == '8':
                self.get_manufacturers_not_supplied_by_supplier(conn)
            elif choice == '9':
                print("Logging out...")
                logged_in = False
            else:
                print("Invalid choice. Please try again.")

    def view_products_types(self, conn):
        Screens.clear_terminal()
        print("Browse Product Types:\n")
        browse_product_types = ProductService.get_product_types(conn)
        if browse_product_types is None:
            print("Product Type is Empty")
        else:
            content = [t.get_content() for t in browse_product_types]
            Screens.print_table(browse_product_types[0].get_header(), content)
            # for browse_product_type in browse_product_types:
            #     browse_product_type.display()
        input("\nPress any key to go to main menu: ")

    def generate_ingredient_list(self, conn):
        Screens.clear_terminal()
        print("Generate Ingredient List:\n")
        product_batches = ProductBatchService.get_all_product_batches(conn)
        if product_batches is None:
            print("No product batch present")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(product_batches)):
            print(f"{i+1}. ", end="")
            product_batches[i].display()
        index = int(input("Select the product batch: ")) - 1
        if index < 0 or index > len(product_batches):
            print("Invalid selection.")
            input("\nPress any key to go to main menu: ")
            return
        product_batch = product_batches[index]
        ingredient_list = IngredientService.get_ingredient_list(conn, product_batch.product_lot_number)
        if ingredient_list is None:
            print("No ingredients to display")
        content = [t.get_content() for t in ingredient_list]
        Screens.print_table(ingredient_list[0].get_header(), content)
        # for ingredient in ingredient_list:
        #     ingredient.display()
        input("\nPress any key to go to main menu: ")

    def get_do_not_combine_pairs(self, conn):
        Screens.clear_terminal()
        print("Product Types for Incompatibilities:\n")
        manufacturers = ManufacturerService.get_all_manufacturers(conn)
        if manufacturers is None:
            print("No manufacturer present")
            input("\nPress any key to go to main menu: ")
            return
        # First Manufacturer
        for i in range(len(manufacturers)):
            print(f"{i+1}. {manufacturers[i].manufacturer_name}")
        index = int(input("Select the first manufacturer: ")) - 1
        if index < 0 or index > len(manufacturers):
            print("Invalid manufacturer selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer_1 = manufacturers[index]
        # First Manufacturer Product
        manufacturer_products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer_1.manufacturer_id)
        for i in range(len(manufacturer_products)):
            print(f"{i+1}. {manufacturer_products[i].product_name}, version: {manufacturer_products[i].version}")
        index = int(input("Select the manufacturer's first product: ")) - 1
        if index < 0 or index > len(manufacturer_products):
            print("Invalid manufacturer product selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer_product_1 = manufacturer_products[index]
        # Second Manufacturer
        for i in range(len(manufacturers)):
            print(f"{i+1}. {manufacturers[i].manufacturer_name}")
        index = int(input("Select the second manufacturer: ")) - 1
        if index < 0 or index > len(manufacturers):
            print("Invalid manufacturer selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer_2 = manufacturers[index]
        # Second Manufacturer Product
        manufacturer_products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer_2.manufacturer_id)
        for i in range(len(manufacturer_products)):
            print(f"{i+1}. {manufacturer_products[i].product_name}, version: {manufacturer_products[i].version}")
        index = int(input("Select the second manufacturer's product: ")) - 1
        if index < 0 or index > len(manufacturer_products):
            print("Invalid manufacturer product selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer_product_2 = manufacturer_products[index]
        product_incompatibilities = ManufacturerProductService.get_product_incompatibilities(conn, manufacturer_product_1.manufacturer_product_id,
                                                                 manufacturer_product_2.manufacturer_product_id)
        if product_incompatibilities is None:
            print("No incompatibility available")
            input("\nPress any key to go to main menu: ")
            return

        content = [t.get_content() for t in product_incompatibilities]
        Screens.print_table(product_incompatibilities[0].get_header(), content)
        # for product_incompatibility in product_incompatibilities:
        #     product_incompatibility.display()
        input("\nPress any key to go to main menu: ")

    def get_last_batch_of_manufacturer_product(self, conn):
        Screens.clear_terminal()
        print("Last Batch Of Manufacturer Product:\n")
        manufacturers = ManufacturerService.get_all_manufacturers(conn)
        if manufacturers is None:
            print("No manufacturer present")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(manufacturers)):
            print(f"{i+1}. {manufacturers[i].manufacturer_name}")
        index = int(input("Select the first manufacturer: ")) - 1
        if index < 0 or index > len(manufacturers):
            print("Invalid manufacturer selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer = manufacturers[index]
        manufacturer_products = ManufacturerProductService.get_all_products_by_manufacturer(conn, manufacturer.manufacturer_id)
        for i in range(len(manufacturer_products)):
            print(f"{i+1}. {manufacturer_products[i].product_name}, version: {manufacturer_products[i].version}")
        index = int(input("Select the manufacturer's product: ")) - 1
        if index < 0 or index > len(manufacturer_products):
            print("Invalid manufacturer product selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer_product = manufacturer_products[index]
        batch_ingredients = ProductBatchService.get_product_batch_ingredients(conn, manufacturer_product.product_id, manufacturer.manufacturer_id)
        content = [t.get_content() for t in batch_ingredients]
        Screens.print_table(batch_ingredients[0].get_header(), content)
        input("\nPress any key to go to main menu: ")

    def get_supplier_spent_for_manufacturer(self, conn):
        Screens.clear_terminal()
        print("Supplier Spent for a Manufacturer:\n")
        manufacturers = ManufacturerService.get_all_manufacturers(conn)
        if manufacturers is None:
            print("No manufacturer present")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(manufacturers)):
            print(f"{i+1}. {manufacturers[i].manufacturer_name}")
        index = int(input("Select the first manufacturer: ")) - 1
        if index < 0 or index > len(manufacturers):
            print("Invalid manufacturer selection.")
            input("\nPress any key to go to main menu: ")
            return
        manufacturer = manufacturers[index]
        supplier_spent = SupplierService.get_supplier_spend(conn, manufacturer.manufacturer_id)
        if supplier_spent is None:
            print("No supplier spent data available")
            input("\nPress any key to go to main menu: ")
            return
        content = [t.get_content() for t in supplier_spent]
        Screens.print_table(supplier_spent[0].get_header(), content)
        input("\nPress any key to go to main menu: ")

    def get_unit_cost_of_product_with_lot_number(self, conn):
        Screens.clear_terminal()
        print("Calculate Unit Cost Of A Product Using Lot Number")
        product_batches = ProductBatchService.get_all_product_batches(conn)
        if product_batches is None:
            print("No product batch present")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(product_batches)):
            print(f"{i+1}. ", end="")
            product_batches[i].display()
        index = int(input("Select the product batch: ")) - 1
        if index < 0 or index > len(product_batches):
            print("Invalid selection.")
            input("\nPress any key to go to main menu: ")
            return
        product_batch = product_batches[index]
        unit_cost = ProductBatchService.calculate_batch_unit_cost(conn, product_batch.product_lot_number)
        print(f"The Unit Cost for this product in this product lot is: {unit_cost}")
        input("\nPress any key to go to main menu: ")

    def get_conflicting_ingredients_using_product_lot_number(self, conn):
        Screens.clear_terminal()
        print("Conflicting Ingredients Using A Product Lot Number:\n")
        product_batches = ProductBatchService.get_all_product_batches(conn)
        if product_batches is None:
            print("No product batch present")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(product_batches)):
            print(f"{i+1}. ", end="")
            product_batches[i].display()
        index = int(input("Select the product batch: ")) - 1
        if index < 0 or index > len(product_batches):
            print("Invalid selection.")
            input("\nPress any key to go to main menu: ")
            return
        product_batch = product_batches[index]
        conflict_ingredients_list = SupplierIngredientService.get_conflicting_ingredients(conn, product_batch.product_lot_number)
        if conflict_ingredients_list is None:
            print("No conflicting ingredients available for the product lot")
            input("\nPress any key to go to main menu: ")
            return
        content = [t.get_content() for t in conflict_ingredients_list]
        Screens.print_table(conflict_ingredients_list[0].get_header(), content)
        input("\nPress any key to go to main menu: ")


    def get_manufacturers_not_supplied_by_supplier(self, conn):
        Screens.clear_terminal()
        print("Manufacturers Not Supplied By A Supplier:\n")
        suppliers = SupplierService.get_all_suppliers(conn)
        if suppliers is None:
            print("No suppliers available")
            input("\nPress any key to go to main menu: ")
            return
        for i in range(len(suppliers)):
            print(f"{i+1}. ", end="")
            suppliers[i].display()
        index = int(input("Select a supplier: ")) - 1
        if index < 0 or index > len(suppliers):
            print("Invalid manufacturer selection.")
            input("\nPress any key to go to main menu: ")
            return
        supplier = suppliers[index]
        unsupplied = ManufacturerSupplierService.get_manufacturers_not_supplied_by_supplier(conn, supplier.supplier_id)
        if unsupplied is None:
            print("No manufacturer available")
            input("\nPress any key to go to main menu: ")
            return
        content = [t.get_content() for t in unsupplied]
        Screens.print_table(unsupplied[0].get_header(), content)
        input("\nPress any key to go to main menu: ")