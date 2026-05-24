from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from modules.auth import AuthManager

class EmployeeManager(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.auth = AuthManager()
        self.init_ui()
        self.load_employees()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("إدارة الموظفين")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Add employee form
        form_group = QGroupBox("إضافة موظف جديد")
        form_layout = QVBoxLayout(form_group)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["كاشير", "مدير", "صاحب"])
        
        add_btn = QPushButton("إضافة موظف")
        add_btn.clicked.connect(self.add_employee)
        
        form_layout.addWidget(QLabel("اسم المستخدم:"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("كلمة المرور:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(QLabel("الدور:"))
        form_layout.addWidget(self.role_combo)
        form_layout.addWidget(add_btn)
        
        layout.addWidget(form_group)
        
        # Employees table
        table_group = QGroupBox("الموظفين الحاليين")
        table_layout = QVBoxLayout(table_group)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(3)
        self.employees_table.setHorizontalHeaderLabels(["اسم المستخدم", "الدور", "الحالة"])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(self.employees_table)
        layout.addWidget(table_group)
        
        self.setLayout(layout)
    
    def load_employees(self):
        """Load employees from database"""
        employees = self.auth.db.execute("SELECT * FROM employees ORDER BY username")
        
        self.employees_table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            # Username
            item = QTableWidgetItem(employee['username'])
            self.employees_table.setItem(row, 0, item)
            
            # Role
            role_map = {
                'cashier': 'كاشير',
                'manager': 'مدير',
                'owner': 'صاحب'
            }
            role_text = role_map.get(employee['role'], employee['role'])
            item = QTableWidgetItem(role_text)
            self.employees_table.setItem(row, 1, item)
            
            # Status
            status_text = "مفعل" if employee['is_active'] else "معطل"
            item = QTableWidgetItem(status_text)
            self.employees_table.setItem(row, 2, item)
    
    def add_employee(self):
        """Add new employee"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role_text = self.role_combo.currentText()
        
        role_map = {
            'كاشير': 'cashier',
            'مدير': 'manager',
            'صاحب': 'owner'
        }
        role = role_map.get(role_text, 'cashier')
        
        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "خطأ", "كلمة المرور يجب أن تكون 4 أحرف على الأقل")
            return
        
        try:
            self.auth.create_employee(username, password, role)
            self.load_employees()
            self.username_input.clear()
            self.password_input.clear()
            QMessageBox.information(self, "نجاح", "تم إضافة الموظف بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إضافة الموظف: {str(e)}")
