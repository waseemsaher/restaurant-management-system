from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox, QFileDialog, QInputDialog,
                             QDialog, QSplitter, QScrollArea, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt
from modules.menu import MenuManager

class MenuManagerScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.menu_manager = MenuManager()
        self.init_ui()
        self.load_categories()
        self.load_items()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("إدارة القائمة (المنيو)")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(title)
        
        # Horizontal splitter: categories on right, items on left
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Categories section
        cat_widget = QWidget()
        cat_main_layout = QVBoxLayout(cat_widget)
        cat_main_layout.setContentsMargins(0, 0, 0, 0)
        cat_main_layout.setSpacing(4)
        
        categories_group = QGroupBox("الأقسام")
        categories_layout = QVBoxLayout(categories_group)
        categories_layout.setSpacing(3)
        categories_layout.setContentsMargins(8, 8, 8, 8)
        
        add_cat_row = QHBoxLayout()
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("اسم القسم")
        add_category_btn = QPushButton("إضافة")
        add_category_btn.clicked.connect(self.add_category)
        add_cat_row.addWidget(self.category_name_input)
        add_cat_row.addWidget(add_category_btn)
        categories_layout.addLayout(add_cat_row)
        
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["القسم", "الحالة"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.categories_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.categories_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.categories_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        categories_layout.addWidget(self.categories_table)
        
        # Category action buttons
        cat_actions = QHBoxLayout()
        self.edit_category_btn = QPushButton("تعديل")
        self.edit_category_btn.clicked.connect(self.edit_category)
        self.toggle_category_btn = QPushButton("تفعيل/تعطيل")
        self.toggle_category_btn.clicked.connect(self.toggle_category)
        self.delete_category_btn = QPushButton("حذف")
        self.delete_category_btn.setStyleSheet("background-color: #fde8e8; color: #c0392b; border: 1px solid #f5c6cb;")
        self.delete_category_btn.clicked.connect(self.delete_category)
        
        cat_actions.addWidget(self.edit_category_btn)
        cat_actions.addWidget(self.toggle_category_btn)
        cat_actions.addWidget(self.delete_category_btn)
        categories_layout.addLayout(cat_actions)
        
        cat_main_layout.addWidget(categories_group)
        splitter.addWidget(cat_widget)
        
        # Items section
        items_widget = QWidget()
        items_main_layout = QVBoxLayout(items_widget)
        items_main_layout.setContentsMargins(0, 0, 0, 0)
        items_main_layout.setSpacing(4)
        
        items_group = QGroupBox("الأصناف")
        items_layout = QVBoxLayout(items_group)
        items_layout.setSpacing(3)
        items_layout.setContentsMargins(8, 8, 8, 8)
        
        # Item form - compact rows
        form_row1 = QHBoxLayout()
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("اسم الصنف")
        self.item_price_input = QLineEdit()
        self.item_price_input.setPlaceholderText("السعر")
        self.item_price_input.setMaximumWidth(100)
        self.category_combo = QComboBox()
        self.category_combo.addItem("اختر القسم")
        form_row1.addWidget(self.item_name_input)
        form_row1.addWidget(self.item_price_input)
        form_row1.addWidget(self.category_combo)
        items_layout.addLayout(form_row1)
        
        form_row2 = QHBoxLayout()
        add_item_btn = QPushButton("إضافة صنف")
        add_item_btn.clicked.connect(self.add_item)
        form_row2.addStretch()
        form_row2.addWidget(add_item_btn)
        items_layout.addLayout(form_row2)
        
        # Item action buttons
        item_actions = QHBoxLayout()
        self.edit_item_btn = QPushButton("تعديل")
        self.edit_item_btn.clicked.connect(self.edit_item)
        self.toggle_item_btn = QPushButton("تفعيل/تعطيل")
        self.toggle_item_btn.clicked.connect(self.toggle_item)
        self.manage_recipes_btn = QPushButton("الوصفة")
        self.manage_recipes_btn.clicked.connect(self.manage_recipes)
        self.delete_item_btn = QPushButton("حذف")
        self.delete_item_btn.setStyleSheet("background-color: #fde8e8; color: #c0392b; border: 1px solid #f5c6cb;")
        self.delete_item_btn.clicked.connect(self.delete_item)
        
        item_actions.addWidget(self.edit_item_btn)
        item_actions.addWidget(self.toggle_item_btn)
        item_actions.addWidget(self.manage_recipes_btn)
        item_actions.addWidget(self.delete_item_btn)
        items_layout.addLayout(item_actions)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["الصنف", "القسم", "السعر", "الحالة"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        items_layout.addWidget(self.items_table)
        
        items_main_layout.addWidget(items_group)
        splitter.addWidget(items_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter, 1)
    
    def load_categories(self):
        """Load categories from database"""
        categories = self.menu_manager.get_categories()
        
        self.categories_table.setRowCount(len(categories))
        self.category_combo.clear()
        self.category_combo.addItem("اختر القسم")
        
        for row, category in enumerate(categories):
            # Category name
            item = QTableWidgetItem(category['name'])
            self.categories_table.setItem(row, 0, item)
            
            # Status
            status_text = "مفعل" if category['is_active'] else "معطل"
            item = QTableWidgetItem(status_text)
            self.categories_table.setItem(row, 1, item)
            
            # Populate category combo
            self.category_combo.addItem(category['name'], category['id'])
    
    def load_items(self):
        """Load menu items from database"""
        items = self.menu_manager.get_items()
        
        self.items_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Item name
            item_widget = QTableWidgetItem(item['name'])
            self.items_table.setItem(row, 0, item_widget)
            
            # Category
            category_name = item['category_name']
            item_widget = QTableWidgetItem(category_name)
            self.items_table.setItem(row, 1, item_widget)
            
            # Price
            item_widget = QTableWidgetItem(str(item['price']))
            self.items_table.setItem(row, 2, item_widget)
            
            # Status
            status_text = "متاح" if item['is_available'] else "غير متاح"
            item_widget = QTableWidgetItem(status_text)
            self.items_table.setItem(row, 3, item_widget)

    def add_category(self):
        """Add new category"""
        name = self.category_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم القسم")
            return
        
        try:
            self.menu_manager.add_category(name)
            self.load_categories()
            self.category_name_input.clear()
            QMessageBox.information(self, "نجاح", "تم إضافة القسم بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة القسم: {str(e)}")

    def edit_category(self):
        row = self.categories_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار قسم من الجدول")
            return
        cat_name = self.categories_table.item(row,0).text()
        categories = self.menu_manager.get_categories()
        cat = next((c for c in categories if c['name']==cat_name), None)
        if not cat:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على القسم")
            return
        new_name, ok = QInputDialog.getText(self, "تعديل القسم", "الاسم الجديد:", text=cat_name)
        if ok and new_name.strip():
            self.menu_manager.update_category(cat['id'], new_name.strip())
            self.load_categories()
            QMessageBox.information(self, "نجاح", "تم تعديل القسم")

    def delete_category(self):
        row = self.categories_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار قسم من الجدول")
            return
        cat_name = self.categories_table.item(row,0).text()
        categories = self.menu_manager.get_categories()
        cat = next((c for c in categories if c['name']==cat_name), None)
        if not cat:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على القسم")
            return
            
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف القسم "{cat_name}" نهائياً؟',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.menu_manager.delete_category(cat['id'])
                self.load_categories()
                QMessageBox.information(self, "نجاح", "تم حذف القسم بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))

    def toggle_category(self):
        row = self.categories_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار قسم من الجدول")
            return
        cat_name = self.categories_table.item(row,0).text()
        categories = self.menu_manager.get_categories()
        cat = next((c for c in categories if c['name']==cat_name), None)
        if not cat:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على القسم")
            return
        new_state = 0 if cat['is_active'] else 1
        self.menu_manager.update_category_status(cat['id'], new_state)
        self.load_categories()
        QMessageBox.information(self, "نجاح", "تم تحديث حالة القسم")

    def edit_item(self):
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار صنف من الجدول")
            return
        item_name = self.items_table.item(row,0).text()
        items = self.menu_manager.get_items()
        itm = next((i for i in items if i['name']==item_name), None)
        if not itm:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على الصنف")
            return
            
        categories = self.menu_manager.get_categories()
        dlg = EditMenuItemDialog(itm, categories, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "خطأ", "الاسم مطلوب")
                return
            try:
                new_price = float(data['price'])
                if new_price <= 0:
                    QMessageBox.warning(self, "خطأ", "السعر يجب أن يكون أكبر من الصفر")
                    return
                
                self.menu_manager.update_item(itm['id'], name=data['name'], price=new_price, category_id=data['category_id'])
                self.load_items()
                QMessageBox.information(self, "نجاح", "تم تعديل الصنف")
            except ValueError:
                QMessageBox.warning(self, "خطأ", "السعر غير صالح")

    def delete_item(self):
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار صنف من الجدول")
            return
        item_name = self.items_table.item(row,0).text()
        items = self.menu_manager.get_items()
        itm = next((i for i in items if i['name']==item_name), None)
        if not itm:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على الصنف")
            return
            
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف الصنف "{item_name}" نهائياً؟',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.menu_manager.delete_item(itm['id'])
                self.load_items()
                QMessageBox.information(self, "نجاح", "تم حذف الصنف بنجاح")
            except Exception as e:
                # If it's a foreign key constraint from order history, we advise disabling it instead
                if 'FOREIGN KEY constraint failed' in str(e) or 'IntegrityError' in str(e) or 'constraint' in str(e).lower():
                    QMessageBox.warning(self, "خطأ", "لا يمكن حذف الصنف لارتباطه بطلبات سابقة. يرجى تعطيله بدلاً من حذفه.")
                else:
                    QMessageBox.warning(self, "خطأ", f"تعذر حذف الصنف: {str(e)}")

    def toggle_item(self):
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار صنف من الجدول")
            return
        item_name = self.items_table.item(row,0).text()
        items = self.menu_manager.get_items()
        itm = next((i for i in items if i['name']==item_name), None)
        if not itm:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على الصنف")
            return
        new_state = 0 if itm['is_available'] else 1
        self.menu_manager.update_item_status(itm['id'], new_state)
        self.load_items()
        QMessageBox.information(self, "نجاح", "تم تحديث حالة الصنف")

    def manage_recipes(self):
        """Open dialog to manage recipes for selected item"""
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار صنف من الجدول")
            return
        item_name = self.items_table.item(row,0).text()
        items = self.menu_manager.get_items()
        itm = next((i for i in items if i['name']==item_name), None)
        if not itm:
            QMessageBox.warning(self, "خطأ", "تعذر العثور على الصنف")
            return

        dlg = RecipeDialog(self.menu_manager, itm['id'], parent=self)
        dlg.exec()
        # reload in case image or other fields changed
        self.load_items()

    def add_item(self):
        """Add new menu item"""
        name = self.item_name_input.text().strip()
        price_text = self.item_price_input.text().strip()
        category_id = self.category_combo.currentData()

        if not name or not price_text or not category_id:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال جميع البيانات")
            return

        try:
            price = float(price_text)
            self.menu_manager.add_item(name, price, category_id)

            self.load_items()
            self.item_name_input.clear()
            self.item_price_input.clear()
            QMessageBox.information(self, "نجاح", "تم إضافة الصنف بنجاح")
        except ValueError:
            QMessageBox.warning(self, "خطأ", "السعر يجب أن يكون رقماً")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة الصنف: {str(e)}")


class RecipeDialog(QDialog):
    def __init__(self, menu_manager: 'MenuManager', item_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إدارة وصفة الصنف')
        self.menu_manager = menu_manager
        self.item_id = item_id
        self.init_ui()
        self.load_recipes()

    def init_ui(self):
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
        from PyQt6.QtWidgets import QLineEdit

        layout = QVBoxLayout()

        # Recipes table
        self.recipes_table = QTableWidget()
        self.recipes_table.setColumnCount(4)
        self.recipes_table.setHorizontalHeaderLabels(['المكونات', 'الكمية', 'الوحدة', ''])
        self.recipes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recipes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.recipes_table)

        # Add new recipe row
        add_layout = QHBoxLayout()
        self.inventory_combo = QComboBox()
        inv = self.menu_manager.get_inventory_items()
        for i in inv:
            self.inventory_combo.addItem(f"{i['name']} ({i.get('unit','')})", i['id'])
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText('الكمية لكل صنف')
        add_btn = QPushButton('إضافة مكون')
        add_btn.clicked.connect(self.add_recipe)
        add_layout.addWidget(QLabel('مكون:'))
        add_layout.addWidget(self.inventory_combo)
        add_layout.addWidget(QLabel('الكمية:'))
        add_layout.addWidget(self.qty_input)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        # Close button
        close_btn = QPushButton('إغلاق')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_recipes(self):
        recipes = self.menu_manager.get_recipes_for_item(self.item_id)
        self.recipes_table.setRowCount(len(recipes))
        for row, r in enumerate(recipes):
            self.recipes_table.setItem(row, 0, QTableWidgetItem(r['inventory_name']))
            self.recipes_table.setItem(row, 1, QTableWidgetItem(str(r['quantity'])))
            self.recipes_table.setItem(row, 2, QTableWidgetItem(r.get('unit','')))
            # delete button
            btn = QPushButton('حذف')
            def make_del(recipe_id):
                def _del():
                    self.menu_manager.delete_recipe(recipe_id)
                    self.load_recipes()
                return _del
            btn.clicked.connect(make_del(r['id']))
            self.recipes_table.setCellWidget(row, 3, btn)

    def add_recipe(self):
        idx = self.inventory_combo.currentIndex()
        inv_id = self.inventory_combo.currentData()
        qty_text = self.qty_input.text().strip()
        try:
            qty = float(qty_text)
            if qty <= 0:
                QMessageBox.warning(self, 'خطأ', 'الكمية يجب أن تكون أكبر من الصفر')
                return
        except ValueError:
            QMessageBox.warning(self, 'خطأ', 'الكمية غير صالحة')
            return
        try:
            self.menu_manager.add_recipe(self.item_id, inv_id, qty)
            self.qty_input.clear()
            self.load_recipes()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة المكون: {str(e)}")

class EditMenuItemDialog(QDialog):
    def __init__(self, item: dict, categories: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle('تعديل صنف')
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(item['name'])
        self.price_input = QLineEdit(str(item['price']))
        self.category_combo = QComboBox()
        
        for c in categories:
            self.category_combo.addItem(c['name'], c['id'])
            if c['id'] == item['category_id']:
                self.category_combo.setCurrentIndex(self.category_combo.count() - 1)
                
        layout.addRow('الاسم:', self.name_input)
        layout.addRow('السعر:', self.price_input)
        layout.addRow('القسم:', self.category_combo)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)
        
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'price': self.price_input.text().strip(),
            'category_id': self.category_combo.currentData()
        }
