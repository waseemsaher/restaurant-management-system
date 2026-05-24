from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt6.QtCore import Qt
from database.db import Database
from datetime import datetime

class ReportsScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
        self.init_ui()
        self.load_report()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("التقارير والإحصائيات")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        self.total_sales_card = QGroupBox("إجمالي مبيعات اليوم")
        card1_layout = QVBoxLayout(self.total_sales_card)
        self.total_sales_label = QLabel("0.00 ج.م")
        self.total_sales_label.setStyleSheet("font-size: 20px; color: #27ae60; font-weight: bold;")
        self.total_sales_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card1_layout.addWidget(self.total_sales_label)
        
        self.total_orders_card = QGroupBox("عدد طلبات اليوم")
        card2_layout = QVBoxLayout(self.total_orders_card)
        self.total_orders_label = QLabel("0")
        self.total_orders_label.setStyleSheet("font-size: 20px; color: #2980b9; font-weight: bold;")
        self.total_orders_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card2_layout.addWidget(self.total_orders_label)
        
        summary_layout.addWidget(self.total_sales_card)
        summary_layout.addWidget(self.total_orders_card)
        
        layout.addLayout(summary_layout)
        
        # Recent orders table
        orders_group = QGroupBox("أحدث الطلبات")
        orders_layout = QVBoxLayout(orders_group)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["رقم الطلب", "الوقت", "المبلغ", "طريقة الدفع"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        orders_layout.addWidget(self.orders_table)
        layout.addWidget(orders_group)
        
        self.setLayout(layout)
    
    def load_report(self):
        """Load today's summary and recent orders"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Total sales and count
        summary = self.db.execute("""
            SELECT SUM(total_amount) as total_sales, COUNT(*) as order_count 
            FROM orders 
            WHERE date(order_time) = date('now', 'localtime') AND is_returned = 0
        """)
        
        if summary and summary[0]['order_count'] > 0:
            self.total_sales_label.setText(f"{summary[0]['total_sales']:.2f} ج.م")
            self.total_orders_label.setText(str(summary[0]['order_count']))
        else:
            self.total_sales_label.setText("0.00 ج.م")
            self.total_orders_label.setText("0")
            
        # Recent orders
        orders = self.db.execute("""
            SELECT * FROM orders 
            ORDER BY order_time DESC 
            LIMIT 50
        """)
        
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['order_number'])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order['order_time']))
            self.orders_table.setItem(row, 2, QTableWidgetItem(f"{order['total_amount']:.2f}"))
            self.orders_table.setItem(row, 3, QTableWidgetItem(order['payment_method']))
