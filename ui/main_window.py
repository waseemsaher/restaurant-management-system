from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QLabel, QMenuBar, QMenu, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from ui.pos import POSScreen
from ui.inventory import InventoryScreen
from ui.employees import EmployeeManager
from ui.reports import ReportsScreen
from ui.settings import SettingsScreen
from ui.menu import MenuManagerScreen
from database.db import Database
from utils.config import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
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
        
        # Settings tab
        self.settings_tab = SettingsScreen(self.user_session)
        self.tabs.addTab(self.settings_tab, "الإعدادات")
        
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
        from PyQt6.QtGui import QAction

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
        is_admin = self.user_session['role'] in ['manager', 'owner']
        tab_index_map = {
            'pos': 0,
            'inventory': 1,
            'menu': 2 if is_admin else -1,
            'employees': 3 if is_admin else -1,
            'reports': 4 if is_admin else 2,
            'settings': 5 if is_admin else 3
        }
        tab_index = tab_index_map.get(tab_name, 0)
        if tab_index != -1:
            self.tabs.setCurrentIndex(tab_index)
    
    def logout(self):
        """Logout current user"""
        from ui.login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()
    
    def open_shift(self):
        """Open new shift: prompt for shift name and create DB record."""
        items = ["صباحي", "مسائي"]
        shift_name, ok = QInputDialog.getItem(self, "بدء شيفت جديد", "اختر الشيفت:", items, 0, False)
        if not ok or not shift_name:
            return

        emp_id = self.user_session.get('id')
        try:
            self.db.execute_non_query(
                "INSERT INTO shifts (employee_id, shift_name, started_at, is_active) VALUES (?, ?, CURRENT_TIMESTAMP, 1)",
                (emp_id, shift_name)
            )
            QMessageBox.information(self, "نجاح", f"تم فتح الشيفت: {shift_name}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح الشيفت: {e}")

        # Refresh shift info
        self.load_current_shift()
    
    def close_shift(self):
        """Close current active shift: compute totals and update DB."""
        emp_id = self.user_session.get('id')
        active = self.db.execute("SELECT * FROM shifts WHERE employee_id = ? AND is_active = 1", (emp_id,))
        if not active:
            QMessageBox.information(self, "ملاحظة", "لا يوجد شيفت مفتوح حالياً")
            return

        shift = active[0]
        # Calculate totals for this shift
        totals = self.db.execute(
            """
            SELECT 
                COUNT(*) as total_orders,
                IFNULL(SUM(total), 0) as total_sales,
                IFNULL(SUM(CASE WHEN payment_method = 'cash' THEN total ELSE 0 END), 0) as cash_collected
            FROM orders
            WHERE shift_id = ? AND status = 'completed'
            """,
            (shift['id'],)
        )
        totals = totals[0] if totals else {'total_orders': 0, 'total_sales': 0.0, 'cash_collected': 0.0}

        try:
            self.db.execute_non_query(
                "UPDATE shifts SET ended_at = CURRENT_TIMESTAMP, total_sales = ?, total_orders = ?, cash_collected = ?, is_active = 0 WHERE id = ?",
                (totals['total_sales'], totals['total_orders'], totals['cash_collected'], shift['id'])
            )
            QMessageBox.information(self, "تم", f"تم إنهاء الشيفت. إجمالي المبيعات: {totals['total_sales']:.2f} - عدد الأوردرات: {totals['total_orders']}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في إنهاء الشيفت: {e}")

        # Refresh shift info
        self.load_current_shift()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "عن البرنامج", 
                          "نظام إدارة المطاعم v1.0\n"
                          "تم التطوير خصيصاً لإدارة المطاعم\n"
                          "جميع الحقوق محفوظة")

    def load_current_shift(self):
        """Load and display the currently active shift for the user."""
        emp_id = self.user_session.get('id')
        try:
            active = self.db.execute("SELECT * FROM shifts WHERE employee_id = ? AND is_active = 1", (emp_id,))
            if not active:
                self.shift_info_label.setText("الشيفت الحالي: لا يوجد شيفت مفتوح")
                return
            shift = active[0]
            started = shift.get('started_at', '')
            self.shift_info_label.setText(f"الشيفت الحالي: {shift.get('shift_name')}  —  بدأ: {started}")
        except Exception:
            self.shift_info_label.setText("")
