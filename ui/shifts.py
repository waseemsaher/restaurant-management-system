from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from modules.shifts import ShiftsManager
from ui.components.shift_dialog import ShiftDetailsDialog


class ShiftsScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.manager = ShiftsManager()
        self.shifts_data = []
        self.init_ui()
        self.load_shifts()

    def init_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QVBoxLayout(self)

        title = QLabel("الشيفتات")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(date.today().replace(day=1))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(date.today())
        filter_btn = QPushButton("عرض")
        filter_btn.clicked.connect(self.load_shifts)
        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(filter_btn)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["التاريخ", "الشيفت", "الموظف", "المبيعات", "الأوردرات", "المعرف"])
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        details_btn = QPushButton("عرض التفاصيل")
        details_btn.clicked.connect(self.open_details)
        print_btn = QPushButton("طباعة")
        print_btn.clicked.connect(self.print_selected_summary)
        actions.addWidget(details_btn)
        actions.addWidget(print_btn)
        layout.addLayout(actions)

    def load_shifts(self):
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        self.shifts_data = self.manager.get_completed_shifts(from_date, to_date)
        self.table.setRowCount(len(self.shifts_data))
        for row, shift in enumerate(self.shifts_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(shift["start_time"])[:10]))
            self.table.setItem(row, 1, QTableWidgetItem(shift.get("shift_type", "")))
            self.table.setItem(row, 2, QTableWidgetItem(shift.get("username", "")))
            self.table.setItem(row, 3, QTableWidgetItem(f"{shift.get('total_sales', 0):.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(shift.get("total_orders", 0))))
            self.table.setItem(row, 5, QTableWidgetItem(str(shift["id"])))

    def selected_shift_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 5).text())

    def open_details(self):
        shift_id = self.selected_shift_id()
        if not shift_id:
            QMessageBox.information(self, "تنبيه", "اختر شيفت أولاً")
            return
        summary = self.manager.get_shift_summary(shift_id)
        dialog = ShiftDetailsDialog(summary, self)
        dialog.exec()

    def print_selected_summary(self):
        shift_id = self.selected_shift_id()
        if not shift_id:
            QMessageBox.information(self, "تنبيه", "اختر شيفت أولاً")
            return
        summary = self.manager.get_shift_summary(shift_id)
        msg = (
            f"تقرير الشيفت {summary.get('shift_type', '-')}\n"
            f"الموظف: {summary.get('username', '-')}\n"
            f"إجمالي المبيعات: {summary.get('total_sales', 0):.2f} ج.م\n"
            f"عدد الأوردرات: {summary.get('order_count', 0)}"
        )
        QMessageBox.information(self, "تقرير الشيفت", msg)
