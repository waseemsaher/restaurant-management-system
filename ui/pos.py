from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox, QSpinBox, QDialog, QDialogButtonBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from modules.orders import OrderManager
from modules.inventory import InventoryManager
from ui.components.invoice_dialog import InvoiceDialog
from datetime import datetime
import os

class POSScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.order_manager = OrderManager()
        self.inventory_manager = InventoryManager()
        self.current_order = []
        self.order_number = self.order_manager.get_next_order_number()
        self.init_ui()
        self.setup_connections()
        self.update_order_number()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Left Side: Category and Item Selection
        left_panel = QVBoxLayout()
        
        # Search Box
        search_card = QFrame()
        search_card.setObjectName("search_card")
        search_card.setStyleSheet("background: white; border-radius: 10px; padding: 10px;")
        search_layout = QHBoxLayout(search_card)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث عن صنف أو كود...")
        self.search_input.setMinimumHeight(40)
        
        search_btn = QPushButton("بحث")
        search_btn.setMinimumHeight(40)
        search_btn.clicked.connect(self.search_items)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        left_panel.addWidget(search_card)
        
        # Categories
        categories_group = QGroupBox("الأقسام")
        categories_layout = QHBoxLayout(categories_group)
        categories_layout.setSpacing(10)
        
        categories = self.order_manager.get_categories()
        for category in categories:
            btn = QPushButton(category['name'])
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self.category_button_clicked)
            btn.setProperty("category_id", category['id'])
            categories_layout.addWidget(btn)
        
        left_panel.addWidget(categories_group)
        
        # Items area: will show item buttons for selected category
        self.items_group = QGroupBox("الأصناف")
        self.items_layout = QHBoxLayout(self.items_group)
        self.items_layout.setSpacing(8)
        self.items_group.setMinimumHeight(240)
        left_panel.addWidget(self.items_group)
        
        # Recent Items / Quick Actions (Optional placeholder)
        left_panel.addStretch()
        
        main_layout.addLayout(left_panel, 2)
        
        # Right Side: Order Summary and Checkout
        right_panel = QVBoxLayout()
        
        # Order Header
        order_header = QFrame()
        order_header.setStyleSheet("background: #2c3e50; color: white; border-radius: 8px;")
        header_layout = QVBoxLayout(order_header)
        
        self.order_label = QLabel(f"رقم الطلب: {self.order_number}")
        self.order_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        
        self.datetime_label = QLabel("")
        self.datetime_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
        
        header_layout.addWidget(self.order_label)
        header_layout.addWidget(self.datetime_label)
        # Order type and table selection
        from utils.config import ConfigManager
        cfg = ConfigManager()
        cfg.load_config()
        if cfg.get('tables.enabled'):
            self.order_type_combo = QComboBox()
            self.order_type_combo.addItems(['takeaway', 'dine-in'])
            header_layout.addWidget(self.order_type_combo)

            # load tables from DB
            tables = self.order_manager.db.execute('SELECT * FROM tables')
            self.table_combo = QComboBox()
            self.table_combo.addItem('اختر طاولة', None)
            for t in tables:
                self.table_combo.addItem(t['table_number'], t['id'])
            header_layout.addWidget(self.table_combo)
        right_panel.addWidget(order_header)
        
        # Order Table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "السعر", "الإجمالي"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_panel.addWidget(self.order_table)
        
        # Summary
        summary_card = QFrame()
        summary_card.setStyleSheet("background: #ecf0f1; border-radius: 8px; padding: 10px;")
        summary_layout = QVBoxLayout(summary_card)
        
        self.total_label = QLabel("الإجمالي: 0.00 ج.م")
        self.total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.total_label)
        
        right_panel.addWidget(summary_card)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        clear_btn = QPushButton("إلغاء")
        clear_btn.setObjectName("clear_btn")
        clear_btn.setMinimumHeight(45)
        clear_btn.clicked.connect(self.clear_order)
        
        delete_btn = QPushButton("حذف الصنف")
        delete_btn.setObjectName("delete_btn")
        delete_btn.setMinimumHeight(45)
        delete_btn.clicked.connect(self.remove_selected_item)
        
        checkout_btn = QPushButton("إتمام الطلب")
        checkout_btn.setObjectName("checkout_btn")
        checkout_btn.setMinimumHeight(45)
        checkout_btn.clicked.connect(self.checkout)
        
        actions_layout.addWidget(clear_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.addWidget(checkout_btn)
        
        right_panel.addLayout(actions_layout)
        
        main_layout.addLayout(right_panel, 1)

    def setup_connections(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.search_input.returnPressed.connect(self.search_items)

    def update_datetime(self):
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def update_order_number(self):
        self.order_label.setText(f"رقم الطلب: {self.order_number}")

    def search_items(self):
        search_term = self.search_input.text().strip()
        if not search_term: return
        items = self.order_manager.search_items(search_term)
        if not items:
            QMessageBox.information(self, "بحث", "لم يتم العثور على أصناف")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("نتائج البحث")
        dialog.setFixedSize(450, 400)
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["الصنف", "القسم", "السعر"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for item in items:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(item['name']))
            table.setItem(row, 1, QTableWidgetItem(item['category_name']))
            table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            table.item(row, 2).setData(Qt.ItemDataRole.UserRole, item['id'])
        
        layout.addWidget(table)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("إضافة للطلب")
        add_btn.clicked.connect(lambda: self.add_from_dialog(table, dialog))
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def add_from_dialog(self, table, dialog):
        selected = table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            item_id = table.item(row, 2).data(Qt.ItemDataRole.UserRole)
            self.add_item_to_order(item_id, 1)
            dialog.accept()

    def category_button_clicked(self):
        sender = self.sender()
        category_id = sender.property("category_id")
        # populate items area with buttons
        items = self.order_manager.get_items_by_category(category_id)
        # clear existing widgets
        for i in reversed(range(self.items_layout.count())):
            w = self.items_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for item in items:
            btn = QPushButton(f"{item['name']}\n{item['price']:.2f} ج.م")
            btn.setMinimumSize(120, 60)
            btn.setProperty('item_id', item['id'])
            btn.clicked.connect(lambda _, bid=item['id']: self.add_item_to_order(bid, 1))
            self.items_layout.addWidget(btn)

    def add_multiple_from_dialog(self, table, dialog):
        selected = table.selectionModel().selectedRows()
        if not selected:
            # If no selection, check if they clicked "Add" anyway, maybe use the focused row?
            # For simplicity, just add the current row if focused
            row = table.currentRow()
            if row >= 0:
                item_id = table.item(row, 1).data(Qt.ItemDataRole.UserRole)
                qty = table.cellWidget(row, 2).value()
                self.add_item_to_order(item_id, qty)
        else:
            for index in selected:
                row = index.row()
                item_id = table.item(row, 1).data(Qt.ItemDataRole.UserRole)
                qty = table.cellWidget(row, 2).value()
                self.add_item_to_order(item_id, qty)
        dialog.accept()

    def add_item_to_order(self, item_id: int, quantity: int):
        item = self.order_manager.get_item(item_id)
        if not item or not item['is_available']:
            QMessageBox.warning(self, "خطأ", "الصنف غير متاح")
            return
        # check all recipe components for availability
        recipes = self.order_manager.get_recipes(item_id)
        for recipe in recipes:
            inv = self.inventory_manager.get_item(recipe['inventory_item_id'])
            if not inv:
                QMessageBox.warning(self, "المخزون", f"مكون {recipe.get('inventory_item_name','?')} غير موجود في المخزون")
                return
            if inv['current_quantity'] < (recipe['quantity'] * quantity):
                QMessageBox.warning(self, "المخزون", f"كمية {inv['name']} لا تكفي")
                return
        
        for i, order_item in enumerate(self.current_order):
            if order_item['id'] == item_id:
                self.current_order[i]['quantity'] += quantity
                self.update_order_table()
                return
        
        self.current_order.append({'id': item_id, 'name': item['name'], 'price': item['price'], 'quantity': quantity})
        self.update_order_table()

    def update_order_table(self):
        self.order_table.setRowCount(len(self.current_order))
        total = 0
        for row, item in enumerate(self.current_order):
            self.order_table.setItem(row, 0, QTableWidgetItem(item['name']))
            # Quantity as spinbox
            spin = QSpinBox()
            spin.setRange(1, 999)
            spin.setValue(item['quantity'])
            spin.setProperty('item_id', item['id'])
            spin.valueChanged.connect(lambda val, s=spin: self.on_quantity_changed(s, val))
            self.order_table.setCellWidget(row, 1, spin)
            self.order_table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            item_total = item['price'] * item['quantity']
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))
            total += item_total
        self.total_label.setText(f"الإجمالي: {total:.2f} ج.م")

    def on_quantity_changed(self, spinbox, value):
        item_id = spinbox.property('item_id')
        for i, it in enumerate(self.current_order):
            if it['id'] == item_id:
                self.current_order[i]['quantity'] = value
                break
        self.update_order_table()

    def remove_selected_item(self):
        row = self.order_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "حذف", "اختر صف لحذفه")
            return
        # confirm
        reply = QMessageBox.question(self, 'تأكيد', 'هل تريد حذف الصنف المحدد؟', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        # determine item id from spinbox in that row
        widget = self.order_table.cellWidget(row, 1)
        if widget:
            item_id = widget.property('item_id')
            self.current_order = [it for it in self.current_order if it['id'] != item_id]
            self.update_order_table()

    def clear_order(self):
        if not self.current_order: return
        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد")
        msg.setText("هل تريد مسح الطلب بالكامل؟")
        yes_btn = msg.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == yes_btn:
            self.current_order = []
            self.update_order_table()

    def checkout(self):
        if not self.current_order: return
        total_text = self.total_label.text().split(": ")[1].split(" ")[0]
        total = float(total_text)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد البيع")
        msg.setText(f"إتمام البيع بمبلغ {total:.2f} ج.م؟")
        yes_btn = msg.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg.exec()
        
        if msg.clickedButton() == yes_btn:
            # determine table and order type if present
            table_id = None
            order_type = 'takeaway'
            if hasattr(self, 'table_combo'):
                table_id = self.table_combo.currentData()
            if hasattr(self, 'order_type_combo'):
                order_type = self.order_type_combo.currentText()

            order_id = self.order_manager.create_order(self.user_session['id'], self.order_number, total, "cash", order_type=order_type, table_id=table_id)
            for item in self.current_order:
                self.order_manager.add_order_item(order_id, item['id'], item['quantity'])
                recipes = self.order_manager.get_recipes(item['id'])
                for recipe in recipes:
                    self.inventory_manager.consume_item(recipe['inventory_item_id'], recipe['quantity'] * item['quantity'])
            
            self.order_manager.update_shift_stats(self.user_session['id'], total)
            self.generate_receipt(order_id)
            self.current_order = []
            self.update_order_table()
            self.order_number = self.order_manager.get_next_order_number()
            self.update_order_number()
            QMessageBox.information(self, "نجاح", "تم إتمام الطلب بنجاح")

    def generate_receipt(self, order_id):
        order = self.order_manager.get_order(order_id)
        items = self.order_manager.get_order_items(order_id)
        dialog = InvoiceDialog(self, order, items)
        dialog.exec()
