from datetime import datetime
from database.db import Database


class ShiftsManager:
    def __init__(self):
        self.db = Database()

    def get_current_shift(self, employee_id: int) -> dict:
        """Backward-compatible alias for active shift."""
        return self.get_active_shift(employee_id)

    def get_active_shift(self, employee_id: int) -> dict:
        """Get current open shift for employee."""
        shifts = self.db.execute(
            """
            SELECT * FROM shifts
            WHERE employee_id = ? AND end_time IS NULL
            ORDER BY start_time DESC
            LIMIT 1
            """,
            (employee_id,),
        )
        return shifts[0] if shifts else {}

    def has_active_shift(self, employee_id: int) -> bool:
        return bool(self.get_active_shift(employee_id))

    def open_shift(self, employee_id: int, shift_type: str = "صباحي", opening_balance: float = 0) -> int:
        """Backward-compatible alias for starting shift."""
        return self.start_shift(employee_id, shift_type, opening_balance)

    def start_shift(self, employee_id: int, shift_type: str, opening_balance: float = 0) -> int:
        """Start a new shift, preventing duplicates."""
        if self.has_active_shift(employee_id):
            raise ValueError("يوجد شيفت مفتوح بالفعل لهذا الموظف")
        self.db.execute_non_query(
            """
            INSERT INTO shifts (employee_id, shift_type, start_time, opening_balance)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            """,
            (employee_id, shift_type, opening_balance),
        )
        return self.db.get_last_insert_id()

    def calculate_shift_totals(self, shift_id: int) -> dict:
        rows = self.db.execute(
            """
            SELECT
                COUNT(*) as total_orders,
                IFNULL(SUM(total_amount), 0) as total_sales,
                IFNULL(SUM(CASE WHEN payment_method='cash' THEN total_amount ELSE 0 END), 0) as cash_collected
            FROM orders
            WHERE shift_id = ? AND IFNULL(is_returned, 0) = 0
            """,
            (shift_id,),
        )
        return rows[0] if rows else {"total_orders": 0, "total_sales": 0.0, "cash_collected": 0.0}

    def close_shift(self, shift_id: int, closing_balance: float | None = None):
        """Backward-compatible close; if balance not passed uses cash total."""
        totals = self.calculate_shift_totals(shift_id)
        if closing_balance is None:
            closing_balance = totals["cash_collected"]
        self.db.execute_non_query(
            """
            UPDATE shifts
            SET end_time = CURRENT_TIMESTAMP,
                total_sales = ?,
                total_orders = ?,
                closing_balance = ?
            WHERE id = ? AND end_time IS NULL
            """,
            (totals["total_sales"], totals["total_orders"], closing_balance, shift_id),
        )

    def end_shift(self, shift_id: int, closing_balance: float | None = None) -> dict:
        totals = self.calculate_shift_totals(shift_id)
        if closing_balance is None:
            closing_balance = totals["cash_collected"]
        self.close_shift(shift_id, closing_balance)
        return totals

    def get_completed_shifts(self, from_date: str | None = None, to_date: str | None = None) -> list:
        query = """
            SELECT s.*, e.username
            FROM shifts s
            JOIN employees e ON e.id = s.employee_id
            WHERE s.end_time IS NOT NULL
        """
        params = []
        if from_date:
            query += " AND date(s.start_time) >= date(?)"
            params.append(from_date)
        if to_date:
            query += " AND date(s.start_time) <= date(?)"
            params.append(to_date)
        query += " ORDER BY s.start_time DESC"
        return self.db.execute(query, tuple(params))

    def get_shift_orders(self, shift_id: int) -> list:
        return self.db.execute(
            """
            SELECT order_number, total_amount, payment_method, order_time
            FROM orders
            WHERE shift_id = ? AND IFNULL(is_returned, 0) = 0
            ORDER BY order_time ASC
            """,
            (shift_id,),
        )

    def get_shift_summary(self, shift_id: int) -> dict:
        shift_data = self.db.execute(
            """
            SELECT s.*, e.username
            FROM shifts s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.id = ?
            """,
            (shift_id,),
        )
        if not shift_data:
            return {}
        shift = shift_data[0]
        totals = self.calculate_shift_totals(shift_id)
        shift["total_sales"] = totals["total_sales"]
        shift["order_count"] = totals["total_orders"]
        shift["cash_collected"] = totals["cash_collected"]
        shift["orders"] = self.get_shift_orders(shift_id)
        shift["duration_text"] = self.format_duration(shift.get("start_time"), shift.get("end_time"))
        return shift

    @staticmethod
    def format_duration(start_time: str | None, end_time: str | None) -> str:
        if not start_time:
            return "-"
        start_dt = datetime.fromisoformat(start_time.replace(" ", "T"))
        end_dt = datetime.now() if not end_time else datetime.fromisoformat(end_time.replace(" ", "T"))
        delta = end_dt - start_dt
        total_minutes = int(delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours} ساعة و {minutes} دقيقة"
