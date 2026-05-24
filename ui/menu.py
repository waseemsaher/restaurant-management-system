from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox, QFileDialog, QInputDialog,
                             QDialog)
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
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("إدارة القائمة (المنيو)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Categories section
        categories_group = QGroupBox("الأقسام")
        categories_layout = QVBoxLayout(categories_group)
        
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("اسم القسم (مثال: كريبات)")
        
        add_category_btn = QPushButton("إضافة قسم")
        add_category_btn.clicked.connect(self.add_category)
        
        categories_layout.addWidget(QLabel("اسم القسم:"))
        categories_layout.addWidget(self.category_name_input)
        categories_layout.addWidget(add_category_btn)
        
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["القسم", "الحالة"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        categories_layout.addWidget(self.categories_table)
        # Category action buttons
        cat_actions = QHBoxLayout()
        self.edit_category_btn = QPushButton("تعديل القسم")
        self.edit_category_btn.clicked.connect(self.edit_category)
        self.toggle_category_btn = QPushButton("تفعيل/تعطيل")
        self.toggle_category_btn.clicked.connect(self.toggle_category)
        cat_actions.addWidget(self.edit_category_btn)
        cat_actions.addWidget(self.toggle_category_btn)
        categories_layout.addLayout(cat_actions)
        
        layout.addWidget(categories_group)
        
        # Items section
        items_group = QGroupBox("الأصناف")
        items_layout = QVBoxLayout(items_group)
        
        # Item form
        form_layout = QVBoxLayout()
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("اسم الصنف (مثال: كريب شيش طاووق)")
        
        self.item_price_input = QLineEdit()
        self.item_price_input.setPlaceholderText("السعر")
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("اختر القسم")
        form_layout.addWidget(QLabel("اسم الصنف:"))
        form_layout.addWidget(self.item_name_input)
        form_layout.addWidget(QLabel("السعر:"))
        form_layout.addWidget(self.item_price_input)
        form_layout.addWidget(QLabel("القسم:"))
        form_layout.addWidget(self.category_combo)
        # Image chooser
        img_choose_layout = QHBoxLayout()
        self.image_path_label = QLabel("")
        choose_img_btn = QPushButton("اختر صورة")
        choose_img_btn.clicked.connect(self.choose_image)
        img_choose_layout.addWidget(choose_img_btn)
        img_choose_layout.addWidget(self.image_path_label)
        form_layout.addLayout(img_choose_layout)
        
        add_item_btn = QPushButton("إضافة صنف")
        add_item_btn.clicked.connect(self.add_item)
        form_layout.addWidget(add_item_btn)
        # Item action buttons
        item_actions = QHBoxLayout()
        self.edit_item_btn = QPushButton("تعديل الصنف")
        self.edit_item_btn.clicked.connect(self.edit_item)
        self.toggle_item_btn = QPushButton("تفعيل/تعطيل الصنف")
        self.toggle_item_btn.clicked.connect(self.toggle_item)
        self.manage_recipes_btn = QPushButton("إدارة الوصفة")
        self.manage_recipes_btn.clicked.connect(self.manage_recipes)
        item_actions.addWidget(self.edit_item_btn)
        item_actions.addWidget(self.toggle_item_btn)
        item_actions.addWidget(self.manage_recipes_btn)
        form_layout.addLayout(item_actions)
        
        items_layout.addLayout(form_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["الصنف", "القسم", "السعر", "الحالة"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(self.items_table)
        
        layout.addWidget(items_group)
        
        self.setLayout(layout)
    
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
            # Image tooltip if available
            img = item.get('image_path')
            if img:
                try:
                    self.items_table.item(row,0).setToolTip(img)
                except Exception:
                    pass

    
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

    def choose_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            self.image_path_label.setText(fname)

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
        new_name, ok1 = QInputDialog.getText(self, "تعديل الصنف", "الاسم:", text=itm['name'])
        if not ok1:
            return
        new_price_text, ok2 = QInputDialog.getText(self, "تعديل الصنف", "السعر:", text=str(itm['price']))
        if not ok2:
            return
        try:
            new_price = float(new_price_text)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "السعر غير صالح")
            return
        self.menu_manager.update_item(itm['id'], name=new_name.strip(), price=new_price)
        self.load_items()
        QMessageBox.information(self, "نجاح", "تم تعديل الصنف")

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

            img = self.image_path_label.text().strip()
            if img:
                from pathlib import Path
                import shutil

                last = self.menu_manager.db.execute("SELECT id FROM menu_items ORDER BY id DESC LIMIT 1")
                if last:
                    item_id = last[0]['id']
                    assets_dir = Path('assets/items')
                    assets_dir.mkdir(parents=True, exist_ok=True)
                    src = Path(img)
                    dest = assets_dir / f"item_{item_id}{src.suffix}"
                    try:
                        shutil.copy(src, dest)
                        self.menu_manager.update_item(item_id, image_path=str(dest))
                    except Exception:
                        pass

            self.load_items()
            self.item_name_input.clear()
            self.item_price_input.clear()
            self.image_path_label.setText("")
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
        except ValueError:
            QMessageBox.warning(self, 'خطأ', 'الكمية غير صالحة')
            return
        try:
            self.menu_manager.add_recipe(self.item_id, inv_id, qty)
            self.qty_input.clear()
            self.load_recipes()
        except ValueError:
            QMessageBox.warning(self, "خطأ", "السعر يجب أن يكون رقماً")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة الصنف: {str(e)}")
