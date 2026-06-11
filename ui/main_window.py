from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QLabel, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from ui.pos import POSScreen
from ui.inventory import InventoryScreen
from ui.employees import EmployeeManager
from ui.reports import ReportsScreen
from ui.settings import SettingsScreen
from ui.menu import MenuManagerScreen
from ui.shifts import ShiftsScreen
from ui.components.shift_dialog import StartShiftDialog, EndShiftDialog
from database.db import Database
from utils.config import ConfigManager
from modules.shifts import ShiftsManager

class MainWindow(QMainWindow):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
        self.shifts_manager = ShiftsManager()
        self.config = ConfigManager()
        # load config (safe)
        try:
            self.config.load_config()
        except Exception:
            pass
        self.init_ui()
        self.setup_menu()
    
    def init_ui(self):
        self.setWindowTitle("نظام إدارة المطاعم")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header / Welcome
        rest_name = self.config.get('restaurant.name', 'مطعمك')
        header_text = f"{rest_name}"
        self.header_label = QLabel(header_text)
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 6px;")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.header_label)

        # Welcome label with user role
        role_map = {
            'cashier': 'كاشير',
            'manager': 'مدير',
            'owner': 'صاحب'
        }
        display_role = role_map.get(self.user_session['role'], self.user_session['role'])
        self.welcome_label = QLabel(f"المستخدم: {self.user_session['username']}  |  الصلاحية: {display_role}")
        self.welcome_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px;")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.welcome_label)

        # Shift info label
        self.shift_info_label = QLabel("")
        self.shift_info_label.setStyleSheet("color: #2c3e50; padding: 4px;")
        self.shift_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.shift_info_label)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # POS tab
        self.pos_tab = POSScreen(self.user_session)
        self.tabs.addTab(self.pos_tab, "الكاشير (نقطة البيع)")
        
        # Inventory tab
        self.inventory_tab = InventoryScreen(self.user_session)
        self.tabs.addTab(self.inventory_tab, "المخزون")
        
        # Menu and Employees tabs (only for manager/owner)
        if self.user_session['role'] in ['manager', 'owner']:
            self.menu_tab = MenuManagerScreen(self.user_session)
            self.tabs.addTab(self.menu_tab, "المنيو")
            
            self.employees_tab = EmployeeManager(self.user_session)
            self.tabs.addTab(self.employees_tab, "الموظفين")
        
        # Reports tab
        self.reports_tab = ReportsScreen(self.user_session)
        self.tabs.addTab(self.reports_tab, "التقارير")

        # Shifts tab
        self.shifts_tab = ShiftsScreen(self.user_session)
        self.tabs.addTab(self.shifts_tab, "الشيفتات")
        
        # Settings tab
        self.settings_tab = SettingsScreen(self.user_session)
        self.tabs.addTab(self.settings_tab, "الإعدادات")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)
        # Load current shift info
        try:
            self.load_current_shift()
        except Exception:
            pass

    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("ملف")
        
        logout_action = QAction("تسجيل الخروج", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Shifts menu
        shifts_menu = menubar.addMenu("الشيفتات")

        open_shift_action = QAction("فتح شيفت جديد", self)
        open_shift_action.triggered.connect(self.open_shift)
        shifts_menu.addAction(open_shift_action)

        close_shift_action = QAction("إغلاق الشيفت الحالي", self)
        close_shift_action.triggered.connect(self.close_shift)
        shifts_menu.addAction(close_shift_action)

        # User menu (shows username + quick actions)
        user_menu = menubar.addMenu("المستخدم")
        user_menu.addAction(f"{self.user_session['username']}")
        logout_action = QAction("تبديل مستخدم / تسجيل خروج", self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("التقارير")
        
        daily_report_action = QAction("تقرير اليوم", self)
        daily_report_action.triggered.connect(lambda: self.switch_tab('reports'))
        reports_menu.addAction(daily_report_action)
        
        # Help menu
        help_menu = menubar.addMenu("مساعدة")
        
        about_action = QAction("عن البرنامج", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def switch_tab(self, tab_name: str):
        """Switch to specified tab"""
        tab_index = self.get_tab_index(tab_name)
        if tab_index != -1:
            self.tabs.setCurrentIndex(tab_index)

    def get_tab_index(self, tab_name: str) -> int:
        is_admin = self.user_session['role'] in ['manager', 'owner']
        tab_index_map = {
            'pos': 0,
            'inventory': 1,
            'menu': 2 if is_admin else -1,
            'employees': 3 if is_admin else -1,
            'reports': 4 if is_admin else 2,
            'shifts': 5 if is_admin else 3,
            'settings': 6 if is_admin else 4
        }
        return tab_index_map.get(tab_name, 0)
    
    def logout(self):
        """Logout current user"""
        from ui.login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()
    
    def open_shift(self):
        """Open new shift using start shift dialog."""
        emp_id = self.user_session.get("id")
        if self.shifts_manager.has_active_shift(emp_id):
            QMessageBox.information(self, "تنبيه", "لا يمكن بدء شيفت جديد قبل إنهاء الشيفت الحالي")
            return
        dialog = StartShiftDialog(self.user_session.get("username", ""), self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            self.shifts_manager.start_shift(emp_id, dialog.selected_shift)
            QMessageBox.information(self, "نجاح", f"تم فتح الشيفت: {dialog.selected_shift}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح الشيفت: {e}")
        self.load_current_shift()
        self.shifts_tab.load_shifts()
    
    def close_shift(self):
        """Close current active shift: compute totals and update DB."""
        emp_id = self.user_session.get("id")
        active_shift = self.shifts_manager.get_active_shift(emp_id)
        if not active_shift:
            QMessageBox.information(self, "ملاحظة", "لا يوجد شيفت مفتوح حالياً")
            return
        totals = self.shifts_manager.calculate_shift_totals(active_shift["id"])
        end_dialog = EndShiftDialog(active_shift, totals, self)
        if end_dialog.exec() != end_dialog.DialogCode.Accepted:
            return
        try:
            self.shifts_manager.end_shift(active_shift["id"], totals["cash_collected"])
            QMessageBox.information(self, "تم", f"تم إنهاء الشيفت. إجمالي المبيعات: {totals['total_sales']:.2f} - عدد الأوردرات: {totals['total_orders']}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنهاء الشيفت: {e}")
        self.load_current_shift()
        self.shifts_tab.load_shifts()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "عن البرنامج", 
                          "نظام إدارة المطاعم v1.0\n"
                          "تم التطوير خصيصاً لإدارة المطاعم\n"
                          "جميع الحقوق محفوظة")

    def load_current_shift(self):
        """Load and display the currently active shift for the user."""
        emp_id = self.user_session.get("id")
        try:
            shift = self.shifts_manager.get_active_shift(emp_id)
            if not shift:
                self.shift_info_label.setText("الشيفت الحالي: لا يوجد شيفت مفتوح")
                return
            started = shift.get("start_time", "")
            self.shift_info_label.setText(f"الشيفت الحالي: {shift.get('shift_type')}  —  بدأ: {started}")
        except Exception:
            self.shift_info_label.setText("")

    def on_tab_changed(self, index: int):
        if index != 0:
            return
        if self.user_session.get("role") not in ["cashier", "manager", "owner"]:
            return
        active_shift = self.shifts_manager.get_active_shift(self.user_session.get("id"))
        if active_shift:
            return
        QMessageBox.information(self, "تنبيه", "يجب بدء شيفت قبل استخدام شاشة الكاشير")
        self.tabs.setCurrentIndex(self.get_tab_index("shifts"))
