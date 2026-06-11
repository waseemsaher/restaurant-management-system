from database.db import Database
from datetime import datetime, timedelta

class ShiftsManager:
    def __init__(self):
        self.db = Database()
    
    def get_current_shift(self, employee_id: int) -> dict:
        """Get current open shift for employee"""
        # Check for open shifts
        shifts = self.db.execute("""
            SELECT * FROM shifts 
            WHERE employee_id = ? AND is_active = 1
            ORDER BY started_at DESC 
            LIMIT 1
        """, (employee_id,))
        
        return shifts[0] if shifts else {}
    
    def open_shift(self, employee_id: int, shift_name: str = 'صباحي') -> int:
        """Open new shift"""
        query = """
            INSERT INTO shifts (employee_id, shift_name, started_at, is_active) 
            VALUES (?, ?, ?, 1)
        """
        self.db.execute_non_query(query, (employee_id, shift_name, datetime.now()))
        return self.db.get_last_insert_id()
    
    def close_shift(self, shift_id: int, total_sales: float = 0, total_orders: int = 0, cash_collected: float = 0):
        """Close current shift"""
        query = """
            UPDATE shifts 
            SET ended_at = ?, is_active = 0, total_sales = ?, total_orders = ?, cash_collected = ?
            WHERE id = ? AND is_active = 1
        """
        self.db.execute_non_query(query, (datetime.now(), total_sales, total_orders, cash_collected, shift_id))
    
    def get_shift_summary(self, shift_id: int) -> dict:
        """Get shift summary"""
        shift_data = self.db.execute("""
            SELECT s.*, e.username 
            FROM shifts s 
            JOIN employees e ON s.employee_id = e.id 
            WHERE s.id = ?
        """, (shift_id,))
        if not shift_data:
            return {}
            
        shift = shift_data[0]
        
        # Get total sales for this shift
        orders = self.db.execute("""
            SELECT SUM(total_amount) as total_sales, COUNT(*) as order_count 
            FROM orders 
            WHERE shift_id = ? AND is_returned = 0
        """, (shift_id,))
        
        if orders:
            shift['total_sales'] = orders[0]['total_sales'] or 0
            shift['order_count'] = orders[0]['order_count']
        
        return shift
