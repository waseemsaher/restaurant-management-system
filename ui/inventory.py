from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QGroupBox, QComboBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
from modules.inventory import InventoryManager


class EditInventoryDialog(QDialog):
    def __init__(self, parent, item: dict):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("تعديل صنف المخزون")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(360)
        layout = QFormLayout(self)

        self.name_input = QLineEdit(item.get('name', ''))
        self.unit_input = QLineEdit(item.get('unit', ''))
        self.current_qty_input = QLineEdit(str(item.get('current_quantity', 0)))
        self.min_qty_input = QLineEdit('' if item.get('min_quantity') is None else str(item.get('min_quantity')))

        layout.addRow("الاسم:", self.name_input)
        layout.addRow("الوحدة:", self.unit_input)
        layout.addRow("الكمية الحالية:", self.current_qty_input)
        layout.addRow("الحد الأدنى:", self.min_qty_input)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addRow(btn_row)

    def values(self):
        min_qty = self.min_qty_input.text().strip()
        return {
            'name': self.name_input.text().strip(),
            'unit': self.unit_input.text().strip(),
            'current_quantity': float(self.current_qty_input.text().strip()),
            'min_quantity': float(min_qty) if min_qty else None,
        }

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

        # Alert banner
        self.alert_label = QLabel("")
        self.alert_label.setVisible(False)
        self.alert_label.setWordWrap(True)
        self.alert_label.setStyleSheet("background: #fff3cd; color: #8a6d3b; padding: 10px; border: 1px solid #ffeeba; border-radius: 6px;")
        layout.addWidget(self.alert_label)

        # Search row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث في المخزون...")
        self.search_input.textChanged.connect(self.filter_inventory)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)
        
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
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels(["الصنف", "الوحدة", "الكمية", "الحد الأدنى", "الحالة", "آخر تحديث"])
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

        edit_btn = QPushButton("تعديل الصنف")
        edit_btn.clicked.connect(self.edit_selected_item)
        transaction_layout.addWidget(edit_btn)
        
        layout.addWidget(transaction_group)
        
        self.setLayout(layout)
    
    def load_inventory(self):
        """Load inventory items"""
        search_term = self.search_input.text().strip() if hasattr(self, 'search_input') else ''
        items = self.inventory_manager.search_items(search_term) if search_term else self.inventory_manager.get_items()
        self._all_items = items
        low_items = self.inventory_manager.get_low_stock_items()
        if low_items:
            alert_lines = ["⚠️ تنبيه: المواد التالية منخفضة:"]
            for item in low_items:
                alert_lines.append(f"• {item['name']}: {item['current_quantity']:.2f} {item['unit']}")
            self.alert_label.setText("\n".join(alert_lines))
            self.alert_label.setVisible(True)
        else:
            self.alert_label.setVisible(False)
        
        self.inventory_table.setRowCount(len(items))
        self.transaction_item_combo.clear()
        
        for row, item in enumerate(items):
            # Item name
            item_widget = QTableWidgetItem(item['name'])
            item_widget.setData(Qt.ItemDataRole.UserRole, item['id'])
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

            updated_at = item.get('updated_at') or ''
            self.inventory_table.setItem(row, 5, QTableWidgetItem(str(updated_at)))
            
            # Populate transaction combo
            self.transaction_item_combo.addItem(f"{item['name']} ({item['unit']})", item['id'])

    def filter_inventory(self, *args):
        self.load_inventory()
    
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

    def get_selected_item(self):
        row = self.inventory_table.currentRow()
        if row < 0 or not hasattr(self, '_all_items'):
            return None
        name_item = self.inventory_table.item(row, 0)
        if not name_item:
            return None
        selected_id = name_item.data(Qt.ItemDataRole.UserRole)
        if selected_id is None:
            return None
        for item in self._all_items:
            if item['id'] == selected_id:
                return item
        return None

    def edit_selected_item(self):
        item = self.get_selected_item()
        if not item:
            QMessageBox.information(self, "تعديل", "اختر صنفاً أولاً")
            return
        dialog = EditInventoryDialog(self, item)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            values = dialog.values()
            if not values['name'] or not values['unit']:
                QMessageBox.warning(self, "خطأ", "اسم الصنف والوحدة مطلوبان")
                return
            self.inventory_manager.update_item(
                item['id'],
                values['name'],
                values['unit'],
                values['current_quantity'],
                values['min_quantity']
            )
            self.load_inventory()
            QMessageBox.information(self, "نجاح", "تم تعديل الصنف بنجاح")
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
