from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox, QSpinBox, QDialog, QDialogButtonBox, QFrame, QGridLayout, QScrollArea,
                             QSplitter)
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
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Left Side: Splitter layout (like inventory/menu)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)
        
        # Search Box (above splitter)
        search_card = QFrame()
        search_card.setObjectName("search_card")
        search_card.setStyleSheet("background: white; border-radius: 8px; padding: 4px;")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(6, 4, 6, 4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث عن صنف أو كود...")
        self.search_input.setMinimumHeight(32)
        
        search_btn = QPushButton("بحث")
        search_btn.setMinimumHeight(32)
        search_btn.clicked.connect(self.search_items)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        left_panel.addWidget(search_card)
        
        # Horizontal splitter: categories | items
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Categories side
        cat_widget = QWidget()
        cat_main_layout = QVBoxLayout(cat_widget)
        cat_main_layout.setContentsMargins(0, 0, 0, 0)
        cat_main_layout.setSpacing(4)
        
        categories_group = QGroupBox("الأقسام")
        categories_layout = QVBoxLayout(categories_group)
        categories_layout.setSpacing(6)
        categories_layout.setContentsMargins(8, 8, 8, 8)
        
        categories = self.order_manager.get_categories()
        for category in categories:
            btn = QPushButton(category['name'])
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                }
            """)
            btn.clicked.connect(self.category_button_clicked)
            btn.setProperty("category_id", category['id'])
            categories_layout.addWidget(btn)
        
        categories_layout.addStretch()
        cat_main_layout.addWidget(categories_group)
        content_splitter.addWidget(cat_widget)
        
        # Items side
        items_widget = QWidget()
        items_main_layout = QVBoxLayout(items_widget)
        items_main_layout.setContentsMargins(0, 0, 0, 0)
        items_main_layout.setSpacing(4)
        
        items_group = QGroupBox("الأصناف")
        items_inner_layout = QVBoxLayout(items_group)
        items_inner_layout.setContentsMargins(4, 4, 4, 4)
        
        self.items_layout = QGridLayout()
        self.items_layout.setSpacing(6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        items_container = QWidget()
        items_container.setLayout(self.items_layout)
        scroll.setWidget(items_container)
        
        items_inner_layout.addWidget(scroll)
        items_main_layout.addWidget(items_group)
        content_splitter.addWidget(items_widget)
        
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        
        left_panel.addWidget(content_splitter, 1)
        
        main_layout.addLayout(left_panel, 2)
        
        # Right Side: Order Summary and Checkout
        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)
        
        # Order Header
        order_header = QFrame()
        order_header.setStyleSheet("background: #2c3e50; color: white; border-radius: 6px; padding: 4px;")
        header_layout = QVBoxLayout(order_header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(2)
        
        self.order_label = QLabel(f"رقم الطلب: {self.order_number}")
        self.order_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        
        self.datetime_label = QLabel("")
        self.datetime_label.setStyleSheet("font-size: 11px; color: #bdc3c7;")
        
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
        
        # Order Table - now with 5 columns: name, qty, price, total, remove
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "السعر", "الإجمالي", "✕"])
        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 110)
        header.resizeSection(2, 70)
        header.resizeSection(3, 80)
        header.resizeSection(4, 40)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_panel.addWidget(self.order_table, 1)
        
        # Summary
        summary_card = QFrame()
        summary_card.setStyleSheet("background: #ecf0f1; border-radius: 6px; padding: 6px;")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(8, 6, 8, 6)
        summary_layout.setSpacing(4)
        
        self.total_label = QLabel("الإجمالي: 0.00 ج.م")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.total_label)

        checkout_btn = QPushButton("إتمام العملية")
        checkout_btn.setObjectName("checkout_btn")
        checkout_btn.setMinimumHeight(40)
        checkout_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; border-radius: 6px; font-size: 15px;")
        checkout_btn.clicked.connect(self.checkout)

        clear_btn = QPushButton("إلغاء الطلب")
        clear_btn.setObjectName("clear_btn")
        clear_btn.setMinimumHeight(34)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #fde8e8;
                color: #c0392b;
                border: 1px solid #f5c6cb;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #e74c3c;
            }
        """)
        clear_btn.clicked.connect(self.clear_order)

        summary_layout.addWidget(checkout_btn)
        summary_layout.addWidget(clear_btn)
        
        right_panel.addWidget(summary_card)
        
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
        
        # clear existing widgets
        for i in reversed(range(self.items_layout.count())):
            item = self.items_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        row, col = 0, 0
        for item in items:
            btn = QPushButton(f"{item['name']}\n{item['price']:.2f} ج.م")
            btn.setMinimumSize(100, 50)
            btn.setProperty('item_id', item['id'])
            btn.clicked.connect(lambda _, bid=item['id']: self.add_item_to_order(bid, 1))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border: 1px solid #3498db;
                }
            """)
            self.items_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def category_button_clicked(self):
        sender = self.sender()
        category_id = sender.property("category_id")
        # populate items area with buttons
        items = self.order_manager.get_items_by_category(category_id)
        # clear existing widgets
        for i in reversed(range(self.items_layout.count())):
            item = self.items_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        row, col = 0, 0
        for item in items:
            btn = QPushButton(f"{item['name']}\n{item['price']:.2f} ج.م")
            btn.setMinimumSize(100, 50)
            btn.setProperty('item_id', item['id'])
            btn.clicked.connect(lambda _, bid=item['id']: self.add_item_to_order(bid, 1))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border: 1px solid #3498db;
                }
            """)
            self.items_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def add_multiple_from_dialog(self, table, dialog):
        selected = table.selectionModel().selectedRows()
        if not selected:
            row = table.currentRow()
            if row >= 0:
                item_id = table.item(row, 2).data(Qt.ItemDataRole.UserRole)
                self.add_item_to_order(item_id, 1)
        else:
            for index in selected:
                row = index.row()
                item_id = table.item(row, 2).data(Qt.ItemDataRole.UserRole)
                self.add_item_to_order(item_id, 1)
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
            quantity = item['quantity']

            # --- Quantity widget: [+] qty [-] centered ---
            spin_container = QWidget()
            spin_container.setStyleSheet("background: transparent;")
            spin_layout = QHBoxLayout(spin_container)
            spin_layout.setContentsMargins(6, 4, 6, 4)
            spin_layout.setSpacing(4)
            spin_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_plus = QPushButton("+")
            btn_plus.setFixedSize(28, 28)
            btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_plus.setStyleSheet("""
                QPushButton {
                    background-color: #d5f5e3; color: #1e8449;
                    font-weight: bold; border-radius: 14px;
                    font-size: 16px; border: none; padding: 0px;
                }
                QPushButton:hover { background-color: #27ae60; color: white; }
            """)
            btn_plus.clicked.connect(lambda c, bid=item['id'], q=quantity: self.on_quantity_changed_custom(bid, q + 1))

            lbl_qty = QLabel(str(quantity))
            lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_qty.setFixedSize(32, 26)
            lbl_qty.setStyleSheet("""
                background-color: #eaf2f8; color: #2c3e50;
                font-weight: bold; font-size: 14px;
                border-radius: 6px; padding: 0px;
            """)

            btn_minus = QPushButton("−")
            btn_minus.setFixedSize(28, 28)
            btn_minus.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_minus.setStyleSheet("""
                QPushButton {
                    background-color: #fadbd8; color: #c0392b;
                    font-weight: bold; border-radius: 14px;
                    font-size: 16px; border: none; padding: 0px;
                }
                QPushButton:hover { background-color: #e74c3c; color: white; }
            """)
            btn_minus.clicked.connect(lambda c, bid=item['id'], q=quantity: self.on_quantity_changed_custom(bid, q - 1))

            spin_layout.addWidget(btn_plus)
            spin_layout.addWidget(lbl_qty)
            spin_layout.addWidget(btn_minus)

            self.order_table.setCellWidget(row, 1, spin_container)
            self.order_table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            item_total = item['price'] * item['quantity']
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))

            # --- Remove button: subtle, transparent, icon only ---
            rm_container = QWidget()
            rm_container.setStyleSheet("background: transparent;")
            rm_layout = QHBoxLayout(rm_container)
            rm_layout.setContentsMargins(0, 0, 0, 0)
            rm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #bdc3c7; 
                    font-size: 15px; font-weight: bold;
                    border: none; border-radius: 14px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #fadbd8;
                    color: #e74c3c;
                }
            """)
            remove_btn.clicked.connect(lambda c, bid=item['id']: self.remove_item_by_id(bid))
            rm_layout.addWidget(remove_btn)
            self.order_table.setCellWidget(row, 4, rm_container)

            total += item_total

        for r in range(len(self.current_order)):
            self.order_table.setRowHeight(r, 40)
        self.total_label.setText(f"الإجمالي: {total:.2f} ج.م")

    def on_quantity_changed_custom(self, item_id, value):
        if value < 1:
            value = 1
        for i, it in enumerate(self.current_order):
            if it['id'] == item_id:
                self.current_order[i]['quantity'] = value
                break
        self.update_order_table()

    def remove_item_by_id(self, item_id):
        """Remove item from order by its id - no confirmation needed for quick POS flow."""
        self.current_order = [it for it in self.current_order if it['id'] != item_id]
        self.update_order_table()

    def remove_selected_item(self):
        row = self.order_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "حذف", "اختر صف لحذفه")
            return
        if row < len(self.current_order):
            item_id = self.current_order[row]['id']
            self.remove_item_by_id(item_id)

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
        
        # Check for active shift
        emp_id = self.user_session['id']
        active_shift = self.order_manager.db.execute("SELECT id FROM shifts WHERE employee_id = ? AND is_active = 1", (emp_id,))
        if not active_shift:
            QMessageBox.warning(self, "تنبيه", "لا يمكن إتمام الطلب لعدم وجود شيفت مفتوح.")
            return

        total = sum(item['price'] * item['quantity'] for item in self.current_order)
        
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

    def generate_receipt(self, order_id):
        order = self.order_manager.get_order(order_id)
        items = self.order_manager.get_order_items(order_id)
        dialog = InvoiceDialog(self, order, items)
        dialog.exec()
