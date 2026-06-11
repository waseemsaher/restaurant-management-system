import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QLabel, QGroupBox, QMessageBox,
                             QHBoxLayout, QTabWidget, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt
from utils.config import ConfigManager
from utils.backup import BackupManager
from utils.printer import PrinterUtility
from database.db import Database

class SettingsScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.config_manager = ConfigManager()
        self.current_config = self.config_manager.load_config()
        self.db = Database()
        self.backup_manager = BackupManager('restaurant.db') # Assuming db name
        self.printer_util = PrinterUtility(self.current_config)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.tabs = QTabWidget()
        
        # 1. Restaurant Info Tab (Read-only)
        res_tab = QWidget()
        res_layout = QVBoxLayout(res_tab)
        res_group = QGroupBox("بيانات المطعم (للقراءة فقط)")
        res_form = QFormLayout(res_group)
        
        restaurant_config = self.current_config.get('restaurant', {})
        self.name_input = QLineEdit(restaurant_config.get('name', ''))
        self.name_input.setReadOnly(True)
        self.address_input = QLineEdit(restaurant_config.get('address', ''))
        self.address_input.setReadOnly(True)
        self.phone_input = QLineEdit(restaurant_config.get('phone', ''))
        self.phone_input.setReadOnly(True)
        
        res_form.addRow("اسم المطعم:", self.name_input)
        res_form.addRow("العنوان:", self.address_input)
        res_form.addRow("الهاتف:", self.phone_input)
        res_layout.addWidget(res_group)
        res_layout.addStretch()
        self.tabs.addTab(res_tab, "المطعم")
        
        # 2. System Settings Tab (Editable)
        sys_tab = QWidget()
        sys_layout = QVBoxLayout(sys_tab)
        sys_group = QGroupBox("إعدادات النظام")
        sys_form = QFormLayout(sys_group)
        
        self.tables_cb = QCheckBox("تفعيل نظام الطاولات")
        self.printer_cb = QCheckBox("تفعيل الطباعة التلقائية")
        
        # Load from config or db
        self.tables_cb.setChecked(self.current_config.get('tables', {}).get('enabled', False))
        self.printer_cb.setChecked(self.current_config.get('printer', {}).get('enabled', False))
        
        self.printer_combo = QComboBox()
        printers = self.printer_util.get_printers()
        self.printer_combo.addItems(printers)
        saved_printer = self.current_config.get('printer', {}).get('default_printer', '')
        if saved_printer in printers:
            self.printer_combo.setCurrentText(saved_printer)
            
        btn_test_print = QPushButton("طباعة تجريبية")
        btn_test_print.clicked.connect(self.test_print)
        
        self.msg_input = QLineEdit(self.current_config.get('invoice', {}).get('thank_you_message', 'شكرا لزيارتكم'))
        
        sys_form.addRow(self.tables_cb)
        sys_form.addRow(self.printer_cb)
        sys_form.addRow("الطابعة الافتراضية:", self.printer_combo)
        sys_form.addRow("", btn_test_print)
        sys_form.addRow("رسالة الشكر:", self.msg_input)
        sys_layout.addWidget(sys_group)
        
        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        sys_layout.addWidget(save_btn)
        sys_layout.addStretch()
        self.tabs.addTab(sys_tab, "النظام")
        
        # 3. Backup Tab
        bak_tab = QWidget()
        bak_layout = QVBoxLayout(bak_tab)
        
        bak_group = QGroupBox("النسخ الاحتياطي")
        bak_inner_layout = QVBoxLayout(bak_group)
        
        btn_backup = QPushButton("إنشاء نسخة احتياطية جديدة")
        btn_backup.clicked.connect(self.create_backup)
        bak_inner_layout.addWidget(btn_backup)
        
        self.bak_table = QTableWidget()
        self.bak_table.setColumnCount(4)
        self.bak_table.setHorizontalHeaderLabels(["الاسم", "التاريخ", "الحجم", "إجراءات"])
        self.bak_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        bak_inner_layout.addWidget(self.bak_table)
        
        bak_layout.addWidget(bak_group)
        self.tabs.addTab(bak_tab, "النسخ الاحتياطي")
        
        layout.addWidget(self.tabs)
        self.load_backups()
        
    def save_settings(self):
        if self.user_session['role'] not in ['owner', 'manager']:
            QMessageBox.warning(self, "خطأ", "ليس لديك صلاحية لتعديل الإعدادات")
            return
            
        self.current_config.setdefault('tables', {})['enabled'] = self.tables_cb.isChecked()
        self.current_config.setdefault('printer', {})['enabled'] = self.printer_cb.isChecked()
        self.current_config.setdefault('printer', {})['default_printer'] = self.printer_combo.currentText()
        self.current_config.setdefault('invoice', {})['thank_you_message'] = self.msg_input.text().strip()
        
        try:
            self.config_manager.save_config(self.current_config)
            
            # Save settings to DB
            self.db.execute_non_query("REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                                      ('tables_enabled', '1' if self.tables_cb.isChecked() else '0'))
            self.db.execute_non_query("REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                                      ('printer_enabled', '1' if self.printer_cb.isChecked() else '0'))
            self.db.execute_non_query("REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                                      ('default_printer', self.printer_combo.currentText()))
            self.db.execute_non_query("REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                                      ('thank_you_message', self.msg_input.text().strip()))
            
            QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حفظ الإعدادات: {str(e)}")

    def create_backup(self):
        try:
            path = self.backup_manager.create_backup()
            QMessageBox.information(self, "نجاح", f"تم إنشاء نسخة احتياطية بنجاح في:\n{path}")
            self.load_backups()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل إنشاء النسخة: {e}")

    def load_backups(self):
        backups = self.backup_manager.get_backups()
        self.bak_table.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self.bak_table.setItem(i, 0, QTableWidgetItem(b['name']))
            self.bak_table.setItem(i, 1, QTableWidgetItem(b['date']))
            self.bak_table.setItem(i, 2, QTableWidgetItem(b['size']))
            
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_restore = QPushButton("استعادة")
            btn_restore.setStyleSheet("background-color: #f39c12; color: white;")
            btn_restore.clicked.connect(lambda checked, p=b['path']: self.restore_backup(p))
            
            btn_del = QPushButton("حذف")
            btn_del.setStyleSheet("background-color: #e74c3c; color: white;")
            btn_del.clicked.connect(lambda checked, p=b['path']: self.delete_backup(p))
            
            actions_layout.addWidget(btn_restore)
            actions_layout.addWidget(btn_del)
            self.bak_table.setCellWidget(i, 3, actions)

    def restore_backup(self, path):
        reply = QMessageBox.warning(
            self, 'تحذير هام',
            'استعادة النسخة الاحتياطية سيؤدي إلى مسح البيانات الحالية وإحلال البيانات القديمة مكانها. هل أنت متأكد؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.backup_manager.restore_backup(path)
                QMessageBox.information(self, "نجاح", "تم استعادة النسخة الاحتياطية بنجاح. يرجى إعادة تشغيل التطبيق.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل استعادة النسخة: {e}")

    def test_print(self):
        printer_name = self.printer_combo.currentText()
        if not printer_name:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار طابعة أولاً")
            return
            
        try:
            test_order = {'order_number': 'TEST-0001', 'created_at': '2024-01-01 12:00', 'total': 150.0}
            test_items = [{'name': 'Test Item', 'quantity': 2, 'price_at_time': 75.0}]
            img_path = self.printer_util.generate_invoice_image(test_order, test_items, "test_print.png")
            self.printer_util.print_image(img_path, printer_name)
            QMessageBox.information(self, "نجاح", "تم إرسال الطباعة التجريبية للطابعة")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل الطباعة: {e}")

    def delete_backup(self, path):
        reply = QMessageBox.question(
            self, 'تأكيد', 'هل تريد حذف هذه النسخة الاحتياطية؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.backup_manager.delete_backup(path)
                self.load_backups()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل الحذف: {e}")
