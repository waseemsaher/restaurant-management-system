import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDateEdit, QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, QDate
from database.db import Database

class ShiftDetailsDialog(QDialog):
    def __init__(self, shift_id: int, parent=None):
        super().__init__(parent)
        self.shift_id = shift_id
        self.db = Database()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("تفاصيل الشفت")
        self.setMinimumSize(450, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # Load Shift
        shift_data = self.db.execute(
            """SELECT s.*, e.username as emp_name 
               FROM shifts s JOIN employees e ON s.employee_id = e.id 
               WHERE s.id = ?""", (self.shift_id,)
        )
        if not shift_data:
            return
            
        s = shift_data[0]
        
        layout.addWidget(QLabel(f"التاريخ: {s['started_at'][:10] if s['started_at'] else ''}"))
        layout.addWidget(QLabel(f"الشفت: {s['shift_name']}"))
        layout.addWidget(QLabel(f"الموظف: {s['emp_name']}"))
        layout.addWidget(QLabel(f"من: {s['started_at']} إلى: {s['ended_at'] or 'مستمر'}"))
        
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line1)
        
        # Calculate REAL totals from orders table (not from shift table which may be stale)
        real_totals = self.db.execute(
            """SELECT 
               COUNT(*) as total_orders,
               COALESCE(SUM(total_amount), 0) as total_sales,
               COALESCE(SUM(CASE WHEN payment_method='cash' THEN total_amount ELSE 0 END), 0) as cash_collected
               FROM orders 
               WHERE shift_id = ? AND is_returned = 0""",
            (self.shift_id,)
        )
        
        if real_totals and real_totals[0]['total_orders'] > 0:
            total_orders = real_totals[0]['total_orders']
            total_sales = real_totals[0]['total_sales']
            cash_coll = real_totals[0]['cash_collected']
        else:
            total_orders = 0
            total_sales = 0.0
            cash_coll = 0.0
        
        avg = total_sales / total_orders if total_orders > 0 else 0.0
        
        layout.addWidget(QLabel(f"إجمالي المبيعات: {total_sales:.2f} ج.م"))
        layout.addWidget(QLabel(f"عدد الأوردرات: {total_orders}"))
        layout.addWidget(QLabel(f"متوسط الأوردر: {avg:.2f} ج.م"))
        layout.addWidget(QLabel(f"كاش محصل: {cash_coll:.2f} ج.م"))
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line2)
        
        layout.addWidget(QLabel("📋 الأوردرات:"))
        
        # Orders table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["رقم الأوردر", "الإجمالي", "طريقة الدفع"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        orders = self.db.execute(
            "SELECT order_number, total_amount, payment_method FROM orders WHERE shift_id = ? AND is_returned=0 ORDER BY id",
            (self.shift_id,)
        )
        self.table.setRowCount(len(orders))
        for i, o in enumerate(orders):
            self.table.setItem(i, 0, QTableWidgetItem(str(o['order_number'])))
            self.table.setItem(i, 1, QTableWidgetItem(f"{o['total_amount']:.2f} ج.م"))
            self.table.setItem(i, 2, QTableWidgetItem(o.get('payment_method', 'cash')))
            
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        print_btn = QPushButton("طباعة")
        print_btn.clicked.connect(lambda: QMessageBox.information(self, "طباعة", "تم الإرسال للطباعة"))
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class ShiftsWindow(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
        self.init_ui()
        
    def init_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        self.btn_filter = QPushButton("عرض")
        self.btn_filter.clicked.connect(self.load_shifts)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "التاريخ", "الشفت", "الموظف", "المبيعات", "الأوردرات", "كاش محصل", "عرض"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Hide ID column
        self.table.setColumnHidden(0, True)
        
        layout.addWidget(self.table)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_details = QPushButton("عرض التفاصيل")
        btn_details.clicked.connect(self.show_details)
        btn_print = QPushButton("طباعة")
        btn_print.clicked.connect(lambda: QMessageBox.information(self, "طباعة", "تم الإرسال للطباعة"))
        
        btn_layout.addWidget(btn_details)
        btn_layout.addWidget(btn_print)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_shifts()
        
    def load_shifts(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        d_to = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"
        
        shifts = self.db.execute(
            """SELECT s.id, s.started_at, s.shift_name, e.username as emp_name
               FROM shifts s 
               JOIN employees e ON s.employee_id = e.id 
               WHERE s.started_at BETWEEN ? AND ? 
               ORDER BY s.started_at DESC""",
            (d_from, d_to)
        )
        
        self.table.setRowCount(len(shifts))
        for i, s in enumerate(shifts):
            self.table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
            date_str = s['started_at'][:10] if s['started_at'] else ''
            self.table.setItem(i, 1, QTableWidgetItem(date_str))
            self.table.setItem(i, 2, QTableWidgetItem(s['shift_name']))
            self.table.setItem(i, 3, QTableWidgetItem(s['emp_name']))
            
            # Calculate REAL totals from orders (not from shift table)
            real = self.db.execute(
                """SELECT 
                   COUNT(*) as cnt,
                   COALESCE(SUM(total_amount), 0) as sales,
                   COALESCE(SUM(CASE WHEN payment_method='cash' THEN total_amount ELSE 0 END), 0) as cash
                   FROM orders WHERE shift_id = ? AND is_returned = 0""",
                (s['id'],)
            )
            if real and real[0]['cnt'] > 0:
                total_sales = real[0]['sales']
                total_orders = real[0]['cnt']
                cash_collected = real[0]['cash']
            else:
                total_sales = 0.0
                total_orders = 0
                cash_collected = 0.0

            self.table.setItem(i, 4, QTableWidgetItem(f"{total_sales:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(str(total_orders)))
            self.table.setItem(i, 6, QTableWidgetItem(f"{cash_collected:.2f}"))
            
            btn = QPushButton("📄")
            btn.clicked.connect(lambda checked, sid=s['id']: self.show_shift_dialog(sid))
            self.table.setCellWidget(i, 7, btn)

    def show_shift_dialog(self, shift_id):
        dialog = ShiftDetailsDialog(shift_id, self)
        dialog.exec()

    def show_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد شيفت أولاً")
            return
        shift_id = int(self.table.item(row, 0).text())
        self.show_shift_dialog(shift_id)
