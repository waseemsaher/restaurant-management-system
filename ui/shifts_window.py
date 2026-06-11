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
        
        # Totals
        total_sales = s.get('total_sales') or 0.0
        total_orders = s.get('total_orders') or 0
        cash_coll = s.get('cash_collected') or 0.0
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
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["رقم الأوردر", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        orders = self.db.execute("SELECT order_number, total FROM orders WHERE shift_id = ? AND status='completed'", (self.shift_id,))
        self.table.setRowCount(len(orders))
        for i, o in enumerate(orders):
            self.table.setItem(i, 0, QTableWidgetItem(str(o['order_number'])))
            self.table.setItem(i, 1, QTableWidgetItem(f"{o['total']:.2f} ج.م"))
            
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "التاريخ", "الشفت", "الموظف", "المبيعات", "الأوردرات", "عرض"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            """SELECT s.id, s.started_at, s.shift_name, e.username as emp_name,
                      s.total_sales, s.total_orders 
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
            self.table.setItem(i, 4, QTableWidgetItem(f"{s['total_sales'] or 0:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(str(s['total_orders'] or 0)))
            
            btn = QPushButton("📄")
            btn.clicked.connect(lambda checked, sid=s['id']: self.show_shift_dialog(sid))
            self.table.setCellWidget(i, 6, btn)

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
