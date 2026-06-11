from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from modules.shifts import ShiftsManager


class StartShiftDialog(QDialog):
    def __init__(self, employee_name: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("بدء شيفت جديد")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(360)
        self.employee_name = employee_name
        self.selected_shift = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"الموظف: {self.employee_name}"))
        layout.addWidget(QLabel("اختر الشيفت:"))
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["صباحي", "مسائي"])
        layout.addWidget(self.shift_combo)

        buttons = QHBoxLayout()
        start_btn = QPushButton("بدء")
        cancel_btn = QPushButton("إلغاء")
        start_btn.clicked.connect(self._confirm)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(start_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _confirm(self):
        self.selected_shift = self.shift_combo.currentText()
        self.accept()


class EndShiftDialog(QDialog):
    def __init__(self, shift: dict, totals: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إنهاء الشيفت")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumWidth(460)
        self.shift = shift
        self.totals = totals
        self.manager = ShiftsManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        duration = self.manager.format_duration(self.shift.get("start_time"), None)
        avg_order = (self.totals["total_sales"] / self.totals["total_orders"]) if self.totals["total_orders"] else 0
        layout.addWidget(QLabel(f"الشيفت: {self.shift.get('shift_type', '-') }"))
        layout.addWidget(QLabel(f"بدأ الساعة: {self.shift.get('start_time', '-') }"))
        layout.addWidget(QLabel(f"المدة: {duration}"))
        layout.addWidget(QLabel("────────────"))
        layout.addWidget(QLabel(f"إجمالي المبيعات: {self.totals['total_sales']:.2f} ج.م"))
        layout.addWidget(QLabel(f"عدد الأوردرات: {self.totals['total_orders']}"))
        layout.addWidget(QLabel(f"متوسط الأوردر: {avg_order:.2f} ج.م"))
        layout.addWidget(QLabel(f"كاش محصل: {self.totals['cash_collected']:.2f} ج.م"))

        actions = QHBoxLayout()
        print_btn = QPushButton("طباعة التقرير")
        finish_btn = QPushButton("إنهاء الشيفت")
        cancel_btn = QPushButton("إلغاء")
        print_btn.clicked.connect(self.print_report)
        finish_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(print_btn)
        actions.addWidget(finish_btn)
        actions.addWidget(cancel_btn)
        layout.addLayout(actions)

    def print_report(self):
        report_dir = Path("receipts") / "shift_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"shift_{self.shift['id']}_{ts}.txt"
        avg_order = (self.totals["total_sales"] / self.totals["total_orders"]) if self.totals["total_orders"] else 0
        content = (
            f"تقرير شيفت\n"
            f"معرف الشيفت: {self.shift['id']}\n"
            f"النوع: {self.shift.get('shift_type', '-')}\n"
            f"البداية: {self.shift.get('start_time', '-')}\n"
            f"إجمالي المبيعات: {self.totals['total_sales']:.2f}\n"
            f"عدد الأوردرات: {self.totals['total_orders']}\n"
            f"متوسط الأوردر: {avg_order:.2f}\n"
            f"كاش محصل: {self.totals['cash_collected']:.2f}\n"
        )
        report_path.write_text(content, encoding="utf-8")
        QMessageBox.information(self, "تم", f"تم حفظ التقرير: {report_path}")


class ShiftDetailsDialog(QDialog):
    def __init__(self, summary: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تفاصيل الشيفت")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(620, 500)
        self.summary = summary
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        avg_order = (self.summary["total_sales"] / self.summary["order_count"]) if self.summary.get("order_count") else 0
        layout.addWidget(QLabel(f"الشيفت: {self.summary.get('shift_type', '-')}"))
        layout.addWidget(QLabel(f"الموظف: {self.summary.get('username', '-')}"))
        layout.addWidget(QLabel(f"من: {self.summary.get('start_time', '-')} إلى: {self.summary.get('end_time', '-')}"))
        layout.addWidget(QLabel(f"المدة: {self.summary.get('duration_text', '-')}"))
        layout.addWidget(QLabel("────────────"))
        layout.addWidget(QLabel(f"إجمالي المبيعات: {self.summary.get('total_sales', 0):.2f} ج.م"))
        layout.addWidget(QLabel(f"عدد الأوردرات: {self.summary.get('order_count', 0)}"))
        layout.addWidget(QLabel(f"متوسط الأوردر: {avg_order:.2f} ج.م"))
        layout.addWidget(QLabel(f"كاش محصل: {self.summary.get('cash_collected', 0):.2f} ج.م"))

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(3)
        self.orders_table.setHorizontalHeaderLabels(["رقم الأوردر", "الوقت", "القيمة"])
        orders = self.summary.get("orders", [])
        self.orders_table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(order["order_number"])))
            self.orders_table.setItem(i, 1, QTableWidgetItem(order["order_time"]))
            self.orders_table.setItem(i, 2, QTableWidgetItem(f"{order['total_amount']:.2f}"))
        layout.addWidget(self.orders_table)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
