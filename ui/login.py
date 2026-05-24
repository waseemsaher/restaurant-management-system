from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from modules.auth import AuthManager
from utils.styles import get_login_style

class LoginScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager()
        self.init_ui()
        self.setup_connections()
        self.setStyleSheet(self.styleSheet() + get_login_style())
    
    def init_ui(self):
        self.setWindowTitle("تسجيل الدخول - نظام إدارة المطاعم")
        self.setFixedSize(500, 450)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Login card
        self.card = QFrame()
        self.card.setObjectName("login_card")
        self.card.setFixedSize(350, 350)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("دخول النظام")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        
        card_layout.addSpacing(20)
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setMinimumHeight(40)
        card_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        card_layout.addWidget(self.password_input)
        
        card_layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("تسجيل الدخول")
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)
        
        main_layout.addWidget(self.card)
        
        # Footer
        version_label = QLabel("نظام إدارة المطاعم v1.0")
        version_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version_label)
    
    def setup_connections(self):
        self.password_input.returnPressed.connect(self.login)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        user = self.auth.authenticate(username, password)
        if user:
            self.user_session = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
            self.accept_login()
        else:
            QMessageBox.warning(self, "خطأ", "بيانات الدخول غير صحيحة")
            self.password_input.clear()
    
    def accept_login(self):
        from ui.main_window import MainWindow
        self.main_window = MainWindow(self.user_session)
        self.main_window.show()
        self.close()
