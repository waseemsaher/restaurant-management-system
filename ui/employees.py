from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QGroupBox, QSplitter, QInputDialog, QFormLayout)
from PyQt6.QtCore import Qt
from modules.auth import AuthManager
from database.db import Database

class EmployeeManager(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.auth = AuthManager()
        self.db = Database()
        self.init_ui()
        self.load_employees()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("إدارة الموظفين")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(title)
        
        # Splitter: form on right, table on left
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Add employee form + Shift assignment
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Add employee form
        form_group = QGroupBox("إضافة موظف جديد")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["كاشير", "مدير", "صاحب"])
        
        add_btn = QPushButton("إضافة موظف")
        add_btn.setMinimumHeight(35)
        add_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; border-radius: 6px;")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_employee)
        
        form_layout.addRow("اسم المستخدم:", self.username_input)
        form_layout.addRow("كلمة المرور:", self.password_input)
        form_layout.addRow("الدور:", self.role_combo)
        form_layout.addRow("", add_btn)

        left_layout.addWidget(form_group)

        # Shift assignment section
        shift_group = QGroupBox("فتح شيفت لموظف")
        shift_layout = QFormLayout(shift_group)
        shift_layout.setSpacing(10)
        shift_layout.setContentsMargins(10, 10, 10, 10)

        self.shift_emp_combo = QComboBox()
        self.shift_emp_combo.setPlaceholderText("اختر الموظف...")

        self.shift_type_combo = QComboBox()
        self.shift_type_combo.addItems(["صباحي", "مسائي"])

        open_shift_btn = QPushButton("فتح شيفت")
        open_shift_btn.setMinimumHeight(35)
        open_shift_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 6px;")
        open_shift_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_shift_btn.clicked.connect(self.open_shift_for_employee)

        shift_layout.addRow("الموظف:", self.shift_emp_combo)
        shift_layout.addRow("نوع الشيفت:", self.shift_type_combo)
        shift_layout.addRow("", open_shift_btn)

        left_layout.addWidget(shift_group)
        left_layout.addStretch()
        
        splitter.addWidget(left_widget)
        
        # Employees table
        table_group = QGroupBox("الموظفين الحاليين")
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(4, 4, 4, 4)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(5)
        self.employees_table.setHorizontalHeaderLabels(["اسم المستخدم", "الدور", "الحالة", "الشيفت", "إجراءات"])
        header = self.employees_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 200)
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        table_layout.addWidget(self.employees_table)
        
        splitter.addWidget(table_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter, 1)
    
    def load_employees(self):
        """Load employees from database"""
        employees = self.auth.db.execute("SELECT * FROM employees ORDER BY username")
        
        self.employees_table.setRowCount(len(employees))

        # Also refresh the shift employee combo
        self.shift_emp_combo.clear()
        self.shift_emp_combo.addItem("اختر الموظف...", None)
        
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
            is_active = employee['is_active']
            status_text = "مفعل ✅" if is_active else "معطل ❌"
            item = QTableWidgetItem(status_text)
            item.setForeground(Qt.GlobalColor.darkGreen if is_active else Qt.GlobalColor.red)
            self.employees_table.setItem(row, 2, item)

            # Active shift info
            active_shift = self.db.execute(
                "SELECT shift_name, started_at FROM shifts WHERE employee_id = ? AND is_active = 1 LIMIT 1",
                (employee['id'],)
            )
            if active_shift:
                s = active_shift[0]
                shift_text = f"{s['shift_name']} ({s['started_at'][:16] if s['started_at'] else ''})"
            else:
                shift_text = "لا يوجد"
            item = QTableWidgetItem(shift_text)
            self.employees_table.setItem(row, 3, item)

            # Action buttons container
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(6)

            # Toggle active/inactive button
            if is_active:
                toggle_btn = QPushButton("تعطيل")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #fadbd8; color: #c0392b;
                        font-weight: bold; border-radius: 4px; padding: 4px 8px;
                        border: 1px solid #f5c6cb;
                    }
                    QPushButton:hover { background-color: #e74c3c; color: white; }
                """)
            else:
                toggle_btn = QPushButton("تفعيل")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #d5f5e3; color: #1e8449;
                        font-weight: bold; border-radius: 4px; padding: 4px 8px;
                        border: 1px solid #c3e6cb;
                    }
                    QPushButton:hover { background-color: #27ae60; color: white; }
                """)
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.clicked.connect(
                lambda checked, eid=employee['id'], active=is_active: self.toggle_employee(eid, active)
            )
            
            delete_btn = QPushButton("حذف")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fde8e8; color: #c0392b;
                    font-weight: bold; border-radius: 4px; padding: 4px 8px;
                    border: 1px solid #f5c6cb;
                }
                QPushButton:hover { background-color: #c0392b; color: white; }
            """)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(
                lambda checked, eid=employee['id'], name=employee['username']: self.delete_employee(eid, name)
            )
            
            actions_layout.addWidget(toggle_btn)
            actions_layout.addWidget(delete_btn)
            self.employees_table.setCellWidget(row, 4, actions_widget)

            # Add to shift combo (only active employees)
            if is_active:
                self.shift_emp_combo.addItem(f"{employee['username']} ({role_text})", employee['id'])
    
    def delete_employee(self, employee_id: int, username: str):
        """Delete employee account"""
        if employee_id == self.user_session.get('id'):
            QMessageBox.warning(self, "خطأ", "لا يمكنك حذف حسابك الخاص!")
            return

        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف الموظف "{username}" نهائياً؟',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.auth.delete_employee(employee_id)
                self.load_employees()
                QMessageBox.information(self, "نجاح", "تم حذف الموظف بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))

    def toggle_employee(self, employee_id: int, currently_active: bool):
        """Toggle employee active status"""
        # Prevent deactivating yourself
        if employee_id == self.user_session.get('id') and currently_active:
            QMessageBox.warning(self, "خطأ", "لا يمكنك تعطيل حسابك الخاص!")
            return

        new_status = 0 if currently_active else 1
        action_text = "تعطيل" if currently_active else "تفعيل"

        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد")
        msg.setText(f"هل تريد {action_text} هذا الموظف؟")
        yes_btn = msg.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg.exec()

        if msg.clickedButton() == yes_btn:
            try:
                self.auth.update_employee(employee_id, is_active=new_status)
                self.load_employees()
                QMessageBox.information(self, "تم", f"تم {action_text} الموظف بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في {action_text} الموظف: {str(e)}")

    def open_shift_for_employee(self):
        """Open a shift for the selected employee"""
        emp_id = self.shift_emp_combo.currentData()
        if not emp_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار موظف أولاً")
            return

        shift_name = self.shift_type_combo.currentText()
        emp_name = self.shift_emp_combo.currentText()

        # Check if employee already has an active shift
        active = self.db.execute(
            "SELECT * FROM shifts WHERE employee_id = ? AND is_active = 1", (emp_id,)
        )
        if active:
            QMessageBox.warning(self, "تنبيه", f"الموظف {emp_name} لديه شيفت مفتوح بالفعل. يرجى إغلاقه أولاً.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("تأكيد")
        msg.setText(f"فتح شيفت '{shift_name}' للموظف {emp_name}؟")
        yes_btn = msg.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg.exec()

        if msg.clickedButton() == yes_btn:
            try:
                self.db.execute_non_query(
                    "INSERT INTO shifts (employee_id, shift_name, started_at, is_active) VALUES (?, ?, CURRENT_TIMESTAMP, 1)",
                    (emp_id, shift_name)
                )
                QMessageBox.information(self, "نجاح", f"تم فتح شيفت '{shift_name}' للموظف {emp_name}")
                self.load_employees()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في فتح الشيفت: {str(e)}")

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
