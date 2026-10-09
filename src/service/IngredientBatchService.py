from repository import IngredientBatchRepository
from model.IngredientInventory import IngredientInventory
from datetime import datetime

def create_ingredient_batch(conn, supplier_id, ingredient_id, unit_price, pack_size, expiration_date):
    return IngredientBatchRepository.create_ingredient_batch(
                                                            conn, 
                                                            supplier_id, 
                                                            ingredient_id, 
                                                            unit_price, 
                                                            pack_size, 
                                                            datetime.strptime(expiration_date, '%Y-%m-%d').date())
