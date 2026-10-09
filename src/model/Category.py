class Category:
    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name

    def __repr__(self):
        return f"<Category(id={self.category_id}, name={self.category_name})>"
    
    def display(self):
        return f"Category: {self.category_name}"
    