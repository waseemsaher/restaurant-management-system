from database.db import Database
from datetime import datetime

class InventoryManager:
    def __init__(self):
        self.db = Database()
        self.ensure_schema()

    def ensure_schema(self):
        """Add backward-compatible columns if they do not exist."""
        cols = self.db.execute("PRAGMA table_info(inventory_items)")
        col_names = [c['name'] for c in cols]
        if 'updated_at' not in col_names:
            try:
                self.db.execute_non_query("ALTER TABLE inventory_items ADD COLUMN updated_at TIMESTAMP")
            except Exception:
                # Existing DBs may already be mid-migration or read-only in tests.
                pass
    
    def get_items(self) -> list:
        """Get all inventory items"""
        return self.db.execute("SELECT * FROM inventory_items ORDER BY name")

    def search_items(self, search_term: str) -> list:
        """Search inventory items by name."""
        term = f"%{search_term.strip()}%"
        return self.db.execute("SELECT * FROM inventory_items WHERE name LIKE ? ORDER BY name", (term,))
    
    def get_item(self, item_id: int) -> dict:
        """Get inventory item by ID"""
        items = self.db.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
        return items[0] if items else {}
    
    def add_item(self, name: str, unit: str, quantity: float, min_quantity: float = None):
        """Add new inventory item"""
        updated_at = datetime.now()
        query = """
            INSERT INTO inventory_items (name, unit, current_quantity, min_quantity, updated_at) 
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_non_query(query, (name, unit, quantity, min_quantity, updated_at))

    def update_item(self, item_id: int, name: str, unit: str, current_quantity: float, min_quantity: float = None):
        """Update inventory item details"""
        query = """
            UPDATE inventory_items
            SET name = ?, unit = ?, current_quantity = ?, min_quantity = ?, updated_at = ?
            WHERE id = ?
        """
        self.db.execute_non_query(query, (name, unit, current_quantity, min_quantity, datetime.now(), item_id))
    
    def add_transaction(self, item_id: int, quantity: float):
        """Add inventory transaction (purchase)"""
        query = """
            INSERT INTO inventory_transactions (inventory_item_id, transaction_type, quantity) 
            VALUES (?, ?, ?)
        """
        self.db.execute_non_query(query, (item_id, 'purchase', quantity))
        
        # Update current quantity
        current = self.db.execute(
            "SELECT current_quantity FROM inventory_items WHERE id = ?",
            (item_id,)
        )[0]['current_quantity']
        
        new_quantity = current + quantity
        update_query = "UPDATE inventory_items SET current_quantity = ?, updated_at = ? WHERE id = ?"
        self.db.execute_non_query(update_query, (new_quantity, datetime.now(), item_id))
    
    def consume_item(self, item_id: int, quantity: float):
        """Consume item from inventory"""
        query = """
            INSERT INTO inventory_transactions (inventory_item_id, transaction_type, quantity, reference_id) 
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_non_query(query, (item_id, 'consumption', quantity, 0))
        
        # Update current quantity
        current_data = self.db.execute(
            "SELECT current_quantity FROM inventory_items WHERE id = ?",
            (item_id,)
        )
        if not current_data:
            return
            
        current = current_data[0]['current_quantity']
        new_quantity = current - quantity
        update_query = "UPDATE inventory_items SET current_quantity = ?, updated_at = ? WHERE id = ?"
        self.db.execute_non_query(update_query, (new_quantity, datetime.now(), item_id))
    
    def get_low_stock_items(self) -> list:
        """Get items with low stock"""
        return self.db.execute("""
            SELECT * FROM inventory_items 
            WHERE min_quantity IS NOT NULL 
            AND current_quantity <= min_quantity
            ORDER BY current_quantity
        """)
