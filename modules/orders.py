from database.db import Database
from datetime import datetime
from modules.shifts import ShiftsManager

class OrderManager:
    def __init__(self):
        self.db = Database()
        self.shifts_manager = ShiftsManager()
    
    def get_next_order_number(self) -> int:
        """Get next order number"""
        last_order = self.db.execute(
            "SELECT order_number FROM orders ORDER BY id DESC LIMIT 1"
        )
        if last_order:
            return last_order[0]['order_number'] + 1
        return 1000
    
    def get_categories(self) -> list:
        """Get all menu categories"""
        return self.db.execute("SELECT * FROM menu_categories WHERE is_active = 1 ORDER BY name")
    
    def get_items_by_category(self, category_id: int) -> list:
        """Get items by category"""
        return self.db.execute("""
            SELECT mi.*, mc.name as category_name 
            FROM menu_items mi 
            JOIN menu_categories mc ON mi.category_id = mc.id 
            WHERE mi.category_id = ? AND mi.is_available = 1
            ORDER BY mi.name
        """, (category_id,))
    
    def search_items(self, search_term: str) -> list:
        """Search items by name"""
        return self.db.execute("""
            SELECT mi.*, mc.name as category_name 
            FROM menu_items mi 
            JOIN menu_categories mc ON mi.category_id = mc.id 
            WHERE mi.name LIKE ? AND mi.is_available = 1
            ORDER BY mi.name
        """, (f"%{search_term}%",))
    
    def get_item(self, item_id: int) -> dict:
        """Get item by ID"""
        items = self.db.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
        return items[0] if items else {}
    
    def get_recipe(self, item_id: int) -> dict:
        """Get recipe for item"""
        recipes = self.db.execute("""
            SELECT r.*, ii.name as inventory_item_name, ii.unit 
            FROM recipes r 
            JOIN inventory_items ii ON r.inventory_item_id = ii.id 
            WHERE r.item_id = ?
        """, (item_id,))
        return recipes[0] if recipes else {}
    
    def create_order(self, employee_id: int, order_number: int, total_amount: float, payment_method: str) -> int:
        """Create new order"""
        # Get current shift
        shift = self.shifts_manager.get_current_shift(employee_id)
        if not shift:
            # Create a default shift if none exists (though UI should handle this)
            shift_id = self.shifts_manager.open_shift(employee_id)
        else:
            shift_id = shift['id']
            
        query = """
            INSERT INTO orders (order_number, shift_id, employee_id, total_amount, payment_method) 
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_non_query(query, (order_number, shift_id, employee_id, total_amount, payment_method))
        return self.db.get_last_insert_id()
    
    def add_order_item(self, order_id: int, menu_item_id: int, quantity: int):
        """Add item to order"""
        item = self.get_item(menu_item_id)
        if not item:
            return
            
        query = """
            INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_time) 
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_non_query(query, (order_id, menu_item_id, quantity, item['price']))
    
    def get_order(self, order_id: int) -> dict:
        """Get order by ID"""
        orders = self.db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return orders[0] if orders else {}
    
    def get_order_items(self, order_id: int) -> list:
        """Get items for an order"""
        return self.db.execute("""
            SELECT oi.*, mi.name 
            FROM order_items oi 
            JOIN menu_items mi ON oi.menu_item_id = mi.id 
            WHERE oi.order_id = ?
        """, (order_id,))
    
    def update_shift_stats(self, employee_id: int, amount: float):
        """Update shift statistics (total sales and order count)"""
        shift = self.shifts_manager.get_current_shift(employee_id)
        if not shift:
            return
            
        query = """
            UPDATE shifts 
            SET total_sales = total_sales + ?, total_orders = total_orders + 1 
            WHERE id = ?
        """
        self.db.execute_non_query(query, (amount, shift['id']))
