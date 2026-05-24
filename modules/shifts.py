from database.db import Database
from datetime import datetime, timedelta

class ShiftsManager:
    def __init__(self):
        self.db = Database()
    
    def get_current_shift(self, employee_id: int) -> dict:
        """Get current open shift for employee"""
        # Check for open shifts in the last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        shifts = self.db.execute("""
            SELECT * FROM shifts 
            WHERE employee_id = ? 
            AND start_time >= ? 
            AND end_time IS NULL
            ORDER BY start_time DESC 
            LIMIT 1
        """, (employee_id, twenty_four_hours_ago))
        
        return shifts[0] if shifts else {}
    
    def open_shift(self, employee_id: int, shift_type: str = 'morning', opening_balance: float = 0) -> int:
        """Open new shift"""
        query = """
            INSERT INTO shifts (employee_id, shift_type, start_time, opening_balance) 
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_non_query(query, (employee_id, shift_type, datetime.now(), opening_balance))
        return self.db.get_last_insert_id()
    
    def close_shift(self, shift_id: int, closing_balance: float):
        """Close current shift"""
        query = """
            UPDATE shifts 
            SET end_time = ?, closing_balance = ? 
            WHERE id = ? AND end_time IS NULL
        """
        self.db.execute_non_query(query, (datetime.now(), closing_balance, shift_id))
    
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
