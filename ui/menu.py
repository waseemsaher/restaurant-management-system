from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox)
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
        
        add_item_btn = QPushButton("إضافة صنف")
        add_item_btn.clicked.connect(self.add_item)
        form_layout.addWidget(add_item_btn)
        
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
