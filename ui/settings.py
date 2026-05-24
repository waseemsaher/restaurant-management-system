from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QLabel, QGroupBox, QMessageBox,
                             QHBoxLayout)
from PyQt6.QtCore import Qt
from utils.config import ConfigManager

class SettingsScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.config_manager = ConfigManager()
        self.current_config = self.config_manager.load_config()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Title
        title = QLabel("إعدادات النظام")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Restaurant info
        res_group = QGroupBox("بيانات المطعم")
        res_layout = QFormLayout(res_group)
        
        restaurant_config = self.current_config.get('restaurant', {})
        invoice_config = self.current_config.get('invoice', {})

        self.name_input = QLineEdit(restaurant_config.get('name', ''))
        self.address_input = QLineEdit(restaurant_config.get('address', ''))
        self.phone_input = QLineEdit(restaurant_config.get('phone', ''))
        self.currency_input = QLineEdit(restaurant_config.get('currency', 'ج.م'))
        self.footer_input = QLineEdit(
            restaurant_config.get('footer_message') or invoice_config.get('thank_you_message', '')
        )
        
        res_layout.addRow("اسم المطعم:", self.name_input)
        res_layout.addRow("العنوان:", self.address_input)
        res_layout.addRow("الهاتف:", self.phone_input)
        res_layout.addRow("العملة:", self.currency_input)
        res_layout.addRow("رسالة الفاتورة:", self.footer_input)
        
        layout.addWidget(res_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        
        actions_layout.addStretch()
        actions_layout.addWidget(save_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def save_config(self):
        if self.user_session['role'] not in ['owner', 'manager']:
            QMessageBox.warning(self, "خطأ", "ليس لديك صلاحية لتعديل الإعدادات")
            return
            
        self.current_config['restaurant']['name'] = self.name_input.text().strip()
        self.current_config['restaurant']['address'] = self.address_input.text().strip()
        self.current_config['restaurant']['phone'] = self.phone_input.text().strip()
        self.current_config['restaurant']['currency'] = self.currency_input.text().strip()
        self.current_config['restaurant']['footer_message'] = self.footer_input.text().strip()
        self.current_config.setdefault('invoice', {})['thank_you_message'] = self.footer_input.text().strip()
        
        try:
            self.config_manager.save_config(self.current_config)
            QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في حفظ الإعدادات: {str(e)}")
