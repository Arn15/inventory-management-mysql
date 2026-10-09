import json
from service import SupplierIngredientService
from service import SupplierService
from service import IngredientService
from service import IngredientBatchService
from utils import Screens

class SupplierView:
    def run(self, conn, user_id):
        print("Supplier View Running")
        supplier = SupplierService.get_supplier_by_user_id(conn, user_id)
        logged_in = True
        while logged_in:
            Screens.clear_terminal()
            print("\nSupplier Menu:")
            print("1. View Ingredients Supplied")
            print("2. Define a new ingredient")
            print("3. Manage ingredients supplied")
            print("4. Update an existing ingredient")
            print("5. Create Ingredient Batch (for supplied ingredients)")
            print("6. Logout")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.manage_supplies(conn, supplier)
            elif choice == '2':
                self.create_new_ingredient(conn, supplier)
            elif choice == '3':
                self.manage_supplier_ingredient(conn, supplier)
            elif choice == '4':
                self.update_ingredient(conn, supplier)
            elif choice == '5':
                self.create_ingredient_batch(conn, supplier)
            elif choice == '6':
                print("Logging out...")
                logged_in = False
            else:
                print("Invalid choice. Please try again.")

    def manage_supplies(self, conn, supplier):
        Screens.clear_terminal()
        print("Ingredients Supplied By Supplier:")
        ingredients = SupplierIngredientService.get_supplier_ingredients(conn, supplier.supplier_id)
        for ing in ingredients:
            print("- ", end = "")
            ing.display()
        input("\nPress any key to go to main menu: ")

    def create_new_ingredient(self, conn, supplier):
        Screens.clear_terminal()
        print("Create New Ingredient Menu:")
        ingredient_name = input("Enter ingredient name: ")
        is_compound = input("Enter if ingredient is compound (T/F): ").lower() == 't'
        IngredientService.create_new_ingredient(conn, ingredient_name, is_compound)
        input("\nPress any key to go to main menu: ")

    def manage_supplier_ingredient(self, conn, supplier):
        Screens.clear_terminal()
        supplier_ingredients_compliment = SupplierIngredientService.get_supplier_ingredients_compliment(conn, supplier.supplier_id)
        for i in range(len(supplier_ingredients_compliment)):
            print(f"{i+1}. ", end="")
            supplier_ingredients_compliment[i].display()

        index = int(input("Select an ingredient to update: ")) - 1
        if 0 > index or index > len(supplier_ingredients_compliment):
            print("Invalid Selection")
            input("\nPress any key to go to main menu: ")
            return None
        
        ingredient = supplier_ingredients_compliment[index]
        material_list_json  = json.dumps({})
        if ingredient.is_compound:
            material_list_json = self.select_ingredients(conn)

        price_per_pack = float(input("Enter the price per pack: "))
        pack_size = int(input("Enter the pack size: "))
        SupplierIngredientService.create_supplier_ingredient(conn, supplier.supplier_id, ingredient.ingredient_id, ingredient.is_compound, material_list_json, price_per_pack, pack_size)
        input("\nPress any key to go to main menu: ")

    def update_ingredient(self, conn, supplier):
        Screens.clear_terminal()
        print("Update Ingredient Menu:")
        supplier_ingredients = SupplierIngredientService.get_supplier_ingredients(conn, supplier.supplier_id)
        compound_ingredients = [item for item in supplier_ingredients if 
                                    IngredientService.get_ingredient_by_id(conn, item.ingredient_id).is_compound]
        for i in range(len(compound_ingredients)):
            print(f"{i+1}. ", end="")
            compound_ingredients[i].display()
        index = int(input("Select an ingredient to update: ")) - 1
        if 0 <= index < len(compound_ingredients):
            material_list_json = json.dumps({})
            ingredient = IngredientService.get_ingredient_by_id(conn, compound_ingredients[index].ingredient_id)
            if ingredient.is_compound:
                material_list_json = self.select_ingredients(conn)
            
            price_per_pack = float(input("Enter the price per pack: "))
            pack_size = int(input("Enter the pack size: "))
            SupplierIngredientService.create_supplier_ingredient(conn, supplier.supplier_id, 
                                                                 ingredient.ingredient_id, 
                                                                 ingredient.is_compound, material_list_json, price_per_pack, pack_size)
        input("\nPress any key to go to main menu: ")

    def create_ingredient_batch(self, conn, supplier):
        Screens.clear_terminal()
        print("Create Ingredient Batch Menu:")
        supplier_ingredients = SupplierIngredientService.get_supplier_ingredients(conn, supplier.supplier_id)
        for i in range(len(supplier_ingredients)):
            print(f"{i+1}. ", end="")
            supplier_ingredients[i].display()
        ingredient_index = int(input("Select an ingredient to update: ")) - 1
        if 0 <= ingredient_index < len(supplier_ingredients):
            supplier_ingredient = supplier_ingredients[ingredient_index]
            print(f"Selected ingredient: {supplier_ingredient.ingredient_id}")
        else:
            print("Invalid ingredient selection.")
            input("\nPress any key to go to main menu: ")
            return
        unit_price = input("Enter unit price: ")
        pack_size = input("Enter pack size: ")
        expiration_date = input("Enter expiration date (YYYY-mm-dd): ")
        is_batch_created = IngredientBatchService.create_ingredient_batch(
                                                                    conn,
                                                                    supplier.supplier_id,
                                                                    supplier_ingredient.ingredient_id,
                                                                    unit_price, 
                                                                    pack_size, 
                                                                    expiration_date
                                                                    )
        if is_batch_created:
            print(f"Ingredient batch created successfully")
        else:
            print("Failed to create ingredient batch.")
        input("\nPress any key to go to main menu: ")

    def select_ingredients(self, conn):
        # Step 1: Fetch and display all ingredients
        ingredients = IngredientService.get_all_ingredients(conn)
        if ingredients is None:
            print("No ingredients available at the moment")
            input("\nPress any key to go to main menu: ")
            return
        atomic_ingredients = [ingredient for ingredient in ingredients if not ingredient.is_compound]
        print("\n=== Available Ingredients ===")
        for ingredient in atomic_ingredients:
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