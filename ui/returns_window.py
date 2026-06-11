import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QRadioButton, QButtonGroup, QTabWidget, QDateEdit, QFrame)
from PyQt6.QtCore import Qt, QDate
from database.db import Database
from modules.orders import OrderManager
from modules.inventory import InventoryManager

class ReturnsWindow(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
        self.order_manager = OrderManager()
        self.inventory_manager = InventoryManager()
        self.current_order = None
        self.current_items = []
        self.init_ui()
        
    def init_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_return_tab(), "البحث و الاسترجاع")
        self.tabs.addTab(self.create_history_tab(), "سجل المرتجعات")
        
        main_layout.addWidget(self.tabs)
        
    def create_return_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search layout
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("رقم الأوردر:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("مثال: ORD-20240115-0023")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("بحث")
        search_btn.clicked.connect(self.search_order)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        
        # Order info layout
        self.order_info_label = QLabel("📋 الأوردر:")
        layout.addWidget(self.order_info_label)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "السعر", "الإجمالي", "استرجاع"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.itemChanged.connect(self.calculate_refund)
        layout.addWidget(self.items_table)
        
        # Return Type
        type_layout = QVBoxLayout()
        self.radio_group = QButtonGroup(self)
        self.radio_full = QRadioButton("⚫ استرجاع كامل")
        self.radio_full.setChecked(True)
        self.radio_full.toggled.connect(self.on_return_type_changed)
        self.radio_partial = QRadioButton("⚪ استرجاع جزئي")
        self.radio_partial.toggled.connect(self.on_return_type_changed)
        
        self.radio_group.addButton(self.radio_full)
        self.radio_group.addButton(self.radio_partial)
        
        type_layout.addWidget(self.radio_full)
        type_layout.addWidget(self.radio_partial)
        layout.addLayout(type_layout)
        
        # Refund details
        self.refund_label = QLabel("المبلغ المسترجع: 0.00 ج.م")
        self.refund_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.refund_label)
        
        reason_layout = QHBoxLayout()
        reason_layout.addWidget(QLabel("السبب (اختياري):"))
        self.reason_input = QLineEdit()
        reason_layout.addWidget(self.reason_input)
        layout.addLayout(reason_layout)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("تأكيد الاسترجاع")
        self.confirm_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        self.confirm_btn.clicked.connect(self.process_return)
        self.confirm_btn.setEnabled(False)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.clear_form)
        
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        return tab

    def create_history_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        
        btn_filter = QPushButton("عرض")
        btn_filter.clicked.connect(self.load_history)
        filter_layout.addWidget(btn_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "التاريخ", "رقم الأوردر", "النوع", "المبلغ", "الموظف", "السبب"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)
        
        self.load_history()
        return tab

    def search_order(self):
        order_num = self.search_input.text().strip()
        if not order_num:
            return
            
        orders = self.db.execute("SELECT * FROM orders WHERE order_number = ?", (order_num,))
        if not orders:
            QMessageBox.warning(self, "خطأ", "الأوردر غير موجود")
            return
            
        order = orders[0]
        if order['status'] == 'returned':
            QMessageBox.warning(self, "خطأ", "هذا الأوردر تم استرجاعه بالكامل مسبقاً")
            return
            
        self.current_order = order
        self.order_info_label.setText(f"📋 الأوردر: {order['order_number']} | التاريخ: {order['created_at']} | الإجمالي: {order['total']:.2f} ج.م")
        
        # Load items
        items = self.db.execute(
            """SELECT oi.*, mi.name 
               FROM order_items oi 
               JOIN menu_items mi ON oi.menu_item_id = mi.id 
               WHERE oi.order_id = ?""",
            (order['id'],)
        )
        self.current_items = items
        self.update_items_table()
        self.calculate_refund()
        self.confirm_btn.setEnabled(True)

    def update_items_table(self):
        self.items_table.blockSignals(True)
        self.items_table.setRowCount(len(self.current_items))
        for i, item in enumerate(self.current_items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"{item['price_at_time']:.2f}"))
            subtotal = item['quantity'] * item['price_at_time']
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(Qt.CheckState.Checked if self.radio_full.isChecked() else Qt.CheckState.Unchecked)
            self.items_table.setItem(i, 4, checkbox)
        self.items_table.blockSignals(False)

    def on_return_type_changed(self):
        is_full = self.radio_full.isChecked()
        self.items_table.blockSignals(True)
        for i in range(self.items_table.rowCount()):
            item = self.items_table.item(i, 4)
            if item:
                item.setCheckState(Qt.CheckState.Checked if is_full else Qt.CheckState.Unchecked)
        self.items_table.blockSignals(False)
        self.calculate_refund()

    def calculate_refund(self):
        if not self.current_order:
            self.refund_label.setText("المبلغ المسترجع: 0.00 ج.م")
            return
            
        total_refund = 0.0
        for i, item in enumerate(self.current_items):
            cb = self.items_table.item(i, 4)
            if cb and cb.checkState() == Qt.CheckState.Checked:
                total_refund += (item['quantity'] * item['price_at_time'])
                
        self.refund_label.setText(f"المبلغ المسترجع: {total_refund:.2f} ج.م")
        return total_refund

    def process_return(self):
        if not self.current_order: return
        
        return_type = 'full' if self.radio_full.isChecked() else 'partial'
        refund_amount = self.calculate_refund()
        
        if refund_amount <= 0:
            QMessageBox.warning(self, "تنبيه", "يجب تحديد أصناف للاسترجاع")
            return
            
        selected_items = []
        for i, item in enumerate(self.current_items):
            cb = self.items_table.item(i, 4)
            if cb and cb.checkState() == Qt.CheckState.Checked:
                selected_items.append(item)
                
        reason = self.reason_input.text().strip()
        
        reply = QMessageBox.question(self, 'تأكيد', f'هل أنت متأكد من استرجاع مبلغ {refund_amount:.2f} ج.م؟',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        try:
            # Insert return
            self.db.execute_non_query(
                "INSERT INTO returns (order_id, employee_id, return_type, amount, reason) VALUES (?, ?, ?, ?, ?)",
                (self.current_order['id'], self.user_session['id'], return_type, refund_amount, reason)
            )
            
            # If full, update order status
            if return_type == 'full':
                self.db.execute_non_query("UPDATE orders SET status = 'returned' WHERE id = ?", (self.current_order['id'],))
            else:
                # Deduct total from order for partial
                new_total = self.current_order['total'] - refund_amount
                self.db.execute_non_query("UPDATE orders SET total = ? WHERE id = ?", (new_total, self.current_order['id']))
                # Also we should probably remove the returned items from order_items, but partial handling can be complex.
                # For now, just mark the order status if they returned everything. 
                if len(selected_items) == len(self.current_items):
                    self.db.execute_non_query("UPDATE orders SET status = 'returned' WHERE id = ?", (self.current_order['id'],))
            
            # Return inventory
            self.return_inventory(selected_items)
            
            QMessageBox.information(self, "نجاح", f"تم استرجاع {refund_amount:.2f} ج.م بنجاح")
            self.clear_form()
            self.load_history()
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء الاسترجاع: {e}")

    def return_inventory(self, items):
        """Return inventory quantities"""
        for item in items:
            recipes = self.order_manager.get_recipes(item['menu_item_id'])
            for recipe in recipes:
                return_qty = recipe['quantity'] * item['quantity']
                self.db.execute_non_query(
                    "UPDATE inventory SET current_quantity = current_quantity + ? WHERE id = ?",
                    (return_qty, recipe['inventory_item_id'])
                )

    def clear_form(self):
        self.search_input.clear()
        self.current_order = None
        self.current_items = []
        self.order_info_label.setText("📋 الأوردر:")
        self.items_table.setRowCount(0)
        self.refund_label.setText("المبلغ المسترجع: 0.00 ج.م")
        self.reason_input.clear()
        self.confirm_btn.setEnabled(False)

    def load_history(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        d_to = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"
        
        returns = self.db.execute(
            """SELECT r.*, o.order_number, e.username as emp_name
               FROM returns r
               JOIN orders o ON r.order_id = o.id
               JOIN employees e ON r.employee_id = e.id
               WHERE r.created_at BETWEEN ? AND ?
               ORDER BY r.created_at DESC""",
            (d_from, d_to)
        )
        
        self.history_table.setRowCount(len(returns))
        for i, r in enumerate(returns):
            self.history_table.setItem(i, 0, QTableWidgetItem(r['created_at'][:16] if r['created_at'] else ''))
            self.history_table.setItem(i, 1, QTableWidgetItem(r['order_number']))
            rt = "كامل" if r['return_type'] == 'full' else "جزئي"
            self.history_table.setItem(i, 2, QTableWidgetItem(rt))
            self.history_table.setItem(i, 3, QTableWidgetItem(f"{r['amount']:.2f} ج.م"))
            self.history_table.setItem(i, 4, QTableWidgetItem(r['emp_name']))
            self.history_table.setItem(i, 5, QTableWidgetItem(r['reason'] or ''))
