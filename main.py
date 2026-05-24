import os

os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from database.init_db import initialize_database
from modules.auth import AuthManager
from utils.config import ConfigManager
from ui.login import LoginScreen
from utils.styles import get_main_style

def main():
    # 1. Initialize Database
    print("Initializing database...")
    initialize_database()
    
    # 2. Initialize Config
    print("Initializing configuration...")
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # 3. Create default admin if no employees exist
    auth = AuthManager()
    employees = auth.db.execute("SELECT * FROM employees")
    if not employees:
        print("Creating default admin account (admin/admin)...")
        auth.create_employee("admin", "admin", "owner")
    
    # 4. Start UI
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setStyleSheet(get_main_style()) # Apply global professional style
    
    login = LoginScreen()
    login.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
