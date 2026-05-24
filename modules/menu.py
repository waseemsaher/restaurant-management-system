from database.db import Database

class MenuManager:
    def __init__(self):
        self.db = Database()
    
    def get_categories(self) -> list:
        """Get all categories"""
        return self.db.execute("SELECT * FROM menu_categories ORDER BY name")
    
    def add_category(self, name: str):
        """Add new category"""
        query = "INSERT INTO menu_categories (name) VALUES (?)"
        self.db.execute_non_query(query, (name,))
    
    def update_category_status(self, category_id: int, is_active: bool):
        """Update category active status"""
        query = "UPDATE menu_categories SET is_active = ? WHERE id = ?"
        self.db.execute_non_query(query, (is_active, category_id))
    
    def get_items(self) -> list:
        """Get all menu items"""
        return self.db.execute("""
            SELECT mi.*, mc.name as category_name 
            FROM menu_items mi 
            JOIN menu_categories mc ON mi.category_id = mc.id 
            ORDER BY mc.name, mi.name
        """)
    
    def add_item(self, name: str, price: float, category_id: int):
        """Add new menu item"""
        query = """
            INSERT INTO menu_items (name, price, category_id) 
            VALUES (?, ?, ?)
        """
        self.db.execute_non_query(query, (name, price, category_id))
    
    def update_item_status(self, item_id: int, is_available: bool):
        """Update item availability"""
        query = "UPDATE menu_items SET is_available = ? WHERE id = ?"
        self.db.execute_non_query(query, (is_available, item_id))
    
    def get_category_name(self, category_id: int) -> str:
        """Get category name by ID"""
        category = self.db.execute(
            "SELECT name FROM menu_categories WHERE id = ?",
            (category_id,)
        )
        return category[0]['name'] if category else ""
