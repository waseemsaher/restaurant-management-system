import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from database.db import Database

class EndShiftDialog(QDialog):
    def __init__(self, shift_id: int, employee_name: str, shift_name: str, start_time: str, parent=None):
        super().__init__(parent)
        self.shift_id = shift_id
        self.employee_name = employee_name
        self.shift_name = shift_name
        self.start_time = start_time
        self.db = Database()
        
        self.totals = self.calculate_shift_totals(shift_id)
        self.init_ui()
        
    def calculate_shift_totals(self, shift_id):
        """Calculate totals for shift"""
        totals = self.db.execute(
            """SELECT 
               COUNT(*) as total_orders,
               SUM(total_amount) as total_sales,
               SUM(CASE WHEN payment_method='cash' THEN total_amount ELSE 0 END) as cash_collected
               FROM orders 
               WHERE shift_id = ? AND is_returned = 0""",
            (shift_id,)
        )
        if not totals or totals[0]['total_orders'] == 0:
            return {'total_orders': 0, 'total_sales': 0.0, 'cash_collected': 0.0, 'avg_order': 0.0}
        
        t = totals[0]
        t['total_sales'] = t['total_sales'] or 0.0
        t['cash_collected'] = t['cash_collected'] or 0.0
        t['avg_order'] = t['total_sales'] / t['total_orders'] if t['total_orders'] > 0 else 0.0
        return t

    def init_ui(self):
        self.setWindowTitle("إنهاء الشفت")
        self.setMinimumSize(350, 400)
        self.resize(350, 400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # Header Info
        layout.addWidget(QLabel(f"الشفت: {self.shift_name}"))
        layout.addWidget(QLabel(f"الموظف: {self.employee_name}"))
        layout.addWidget(QLabel(f"بدأ الساعة: {self.start_time}"))
        
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line1)
        
        # Summary
        summary_label = QLabel("📊 ملخص الشفت:")
        summary_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(summary_label)
        
        layout.addWidget(QLabel(f"إجمالي المبيعات: {self.totals['total_sales']:.2f} ج.م"))
        layout.addWidget(QLabel(f"عدد الأوردرات: {self.totals['total_orders']}"))
        layout.addWidget(QLabel(f"متوسط الأوردر: {self.totals['avg_order']:.2f} ج.م"))
        layout.addWidget(QLabel(f"كاش محصل: {self.totals['cash_collected']:.2f} ج.م"))
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line2)
        
        # Print Button
        self.print_btn = QPushButton("طباعة التقرير")
        self.print_btn.clicked.connect(self.print_report)
        layout.addWidget(self.print_btn)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.end_btn = QPushButton("إنهاء الشفت")
        self.end_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.end_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.end_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def print_report(self):
        # Placeholder for print
        QMessageBox.information(self, "طباعة", "تم إرسال التقرير للطباعة (قيد التطوير)")
