from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QGroupBox, QComboBox)
from PyQt6.QtCore import Qt
from modules.inventory import InventoryManager

class InventoryScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.inventory_manager = InventoryManager()
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("إدارة المخزون")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Add inventory item form
        form_group = QGroupBox("إضافة صنف جديد للمخزون")
        form_layout = QVBoxLayout(form_group)
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("اسم الصنف (مثال: دقيق، زيت، جبنة)")
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["kg", "g", "l", "ml", "piece", "bag"])
        
        self.initial_quantity_input = QLineEdit()
        self.initial_quantity_input.setPlaceholderText("الكمية الأولية")
        self.initial_quantity_input.setMaxLength(10)
        
        self.min_quantity_input = QLineEdit()
        self.min_quantity_input.setPlaceholderText("الحد الأدنى (تنبيه عند الوصول)")
        self.min_quantity_input.setMaxLength(10)
        
        add_btn = QPushButton("إضافة صنف")
        add_btn.clicked.connect(self.add_inventory_item)
        
        form_layout.addWidget(QLabel("اسم الصنف:"))
        form_layout.addWidget(self.item_name_input)
        form_layout.addWidget(QLabel("وحدة القياس:"))
        form_layout.addWidget(self.unit_combo)
        form_layout.addWidget(QLabel("الكمية الأولية:"))
        form_layout.addWidget(self.initial_quantity_input)
        form_layout.addWidget(QLabel("الحد الأدنى:"))
        form_layout.addWidget(self.min_quantity_input)
        form_layout.addWidget(add_btn)
        
        layout.addWidget(form_group)
        
        # Inventory table
        table_group = QGroupBox("المخزون الحالي")
        table_layout = QVBoxLayout(table_group)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["الصنف", "الوحدة", "الكمية", "الحد الأدنى", "الحالة"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(self.inventory_table)
        
        layout.addWidget(table_group)
        
        # Add inventory transaction form
        transaction_group = QGroupBox("إضافة كمية جديدة (مشتريات)")
        transaction_layout = QVBoxLayout(transaction_group)
        
        self.transaction_item_combo = QComboBox()
        
        self.transaction_quantity_input = QLineEdit()
        self.transaction_quantity_input.setPlaceholderText("الكمية المضافة")
        self.transaction_quantity_input.setMaxLength(10)
        
        add_transaction_btn = QPushButton("إضافة كمية")
        add_transaction_btn.clicked.connect(self.add_inventory_transaction)
        
        transaction_layout.addWidget(QLabel("الصنف:"))
        transaction_layout.addWidget(self.transaction_item_combo)
        transaction_layout.addWidget(QLabel("الكمية المضافة:"))
        transaction_layout.addWidget(self.transaction_quantity_input)
        transaction_layout.addWidget(add_transaction_btn)
        
        layout.addWidget(transaction_group)
        
        self.setLayout(layout)
    
    def load_inventory(self):
        """Load inventory items"""
        items = self.inventory_manager.get_items()
        
        self.inventory_table.setRowCount(len(items))
        self.transaction_item_combo.clear()
        
        for row, item in enumerate(items):
            # Item name
            item_widget = QTableWidgetItem(item['name'])
            self.inventory_table.setItem(row, 0, item_widget)
            
            # Unit
            item_widget = QTableWidgetItem(item['unit'])
            self.inventory_table.setItem(row, 1, item_widget)
            
            # Current quantity
            item_widget = QTableWidgetItem(f"{item['current_quantity']:.2f}")
            self.inventory_table.setItem(row, 2, item_widget)
            
            # Min quantity
            min_q = item['min_quantity']
            item_widget = QTableWidgetItem(f"{min_q:.2f}" if min_q is not None else "")
            self.inventory_table.setItem(row, 3, item_widget)
            
            # Status
            if min_q is not None and item['current_quantity'] <= min_q:
                status = "⚠️ منخفض"
                item_widget = QTableWidgetItem(status)
                item_widget.setForeground(Qt.GlobalColor.red)
            else:
                status = "متوفر"
                item_widget = QTableWidgetItem(status)
                item_widget.setForeground(Qt.GlobalColor.darkGreen)
            self.inventory_table.setItem(row, 4, item_widget)
            
            # Populate transaction combo
            self.transaction_item_combo.addItem(f"{item['name']} ({item['unit']})", item['id'])
    
    def add_inventory_item(self):
        """Add new inventory item"""
        name = self.item_name_input.text().strip()
        unit = self.unit_combo.currentText()
        quantity_text = self.initial_quantity_input.text().strip()
        min_quantity_text = self.min_quantity_input.text().strip()
        
        if not name or not quantity_text:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الصنف والكمية")
            return
        
        try:
            quantity = float(quantity_text)
            min_quantity = float(min_quantity_text) if min_quantity_text else None
            
            self.inventory_manager.add_item(name, unit, quantity, min_quantity)
            self.load_inventory()
            self.item_name_input.clear()
            self.initial_quantity_input.clear()
            self.min_quantity_input.clear()
            QMessageBox.information(self, "نجاح", "تم إضافة الصنف للمخزون")
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الكمية يجب أن تكون رقماً")
    
    def add_inventory_transaction(self):
        """Add inventory transaction (purchase)"""
        item_id = self.transaction_item_combo.currentData()
        if item_id is None:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار صنف")
            return
            
        quantity_text = self.transaction_quantity_input.text().strip()
        
        if not quantity_text:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال الكمية")
            return
        
        try:
            quantity = float(quantity_text)
            self.inventory_manager.add_transaction(item_id, quantity)
            self.load_inventory()
            self.transaction_quantity_input.clear()
            QMessageBox.information(self, "نجاح", "تمت إضافة الكمية للمخزون")
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الكمية يجب أن تكون رقماً")
