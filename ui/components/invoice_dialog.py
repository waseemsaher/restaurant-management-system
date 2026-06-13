from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import os
from datetime import datetime
import subprocess
from utils.config import ConfigManager
from utils.printer import PrinterUtility

class InvoiceDialog(QDialog):
    def __init__(self, parent, order: dict, items: list):
        super().__init__(parent)
        self.order = order
        self.items = items
        self.setWindowTitle("فاتورة")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(420, 480)
        self.config_manager = ConfigManager()
        self.printer_util = PrinterUtility(self.config_manager.load_config())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel(f"<b>{self.order.get('order_number','')} - فاتورة</b>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        info = QLabel(f"التاريخ: {self.order.get('order_time', '')}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(self.format_invoice_text())
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        print_btn = QPushButton("طباعة الفاتورة")
        print_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        print_btn.clicked.connect(self.print_direct)
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def format_invoice_text(self):
        lines = []
        lines.append(f"رقم الطلب: {self.order.get('order_number','')}")
        lines.append(f"التاريخ: {self.order.get('order_time','')}")
        lines.append("=" * 32)
        total = 0
        for it in self.items:
            name = it.get('name')
            qty = it.get('quantity', 0)
            price = it.get('price_at_time', 0)
            subtotal = qty * price
            total += subtotal
            lines.append(f"{name} x{qty}  - {subtotal:.2f} ج.م")
        lines.append("=" * 32)
        lines.append(f"الإجمالي: {total:.2f} ج.م")
        lines.append("")
        lines.append("شكراً لزيارتكم")
        return "\n".join(lines)

    def ensure_receipts_dir(self):
        if not os.path.exists("receipts"):
            os.makedirs("receipts")

    def save_to_file(self):
        self.ensure_receipts_dir()
        filename = f"receipts/invoice_{self.order.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text.toPlainText())
            QMessageBox.information(self, "حفظ", f"تم حفظ الفاتورة في: {filename}")
            return filename
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")
            return None

    def save_and_notify_print(self):
        # Save then instruct user how to print using system tools
        self.save_to_file()
        QMessageBox.information(self, "طباعة", "يمكنك طباعة الملف المحفوظ باستخدام أوامر النظام (مثال: lp أو lpr) أو من مدير الملفات.")

    def print_direct(self):
        # Generate image and print
        self.ensure_receipts_dir()
        filename = f"receipts/invoice_{self.order.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            img_path = self.printer_util.generate_invoice_image(self.order, self.items, filename)
            # check if printer is enabled in config
            cfg = self.config_manager.load_config()
            printer_enabled = cfg.get('printer', {}).get('enabled', False)
            if not printer_enabled:
                QMessageBox.information(self, "طباعة", "الطباعة التلقائية معطلة في الإعدادات. تم حفظ صورة الفاتورة.")
                return
                
            printer_name = cfg.get('printer', {}).get('default_printer')
            self.printer_util.print_image(img_path, printer_name)
            QMessageBox.information(self, "طباعة", "تم إرسال الفاتورة إلى الطابعة.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الطباعة: {e}")
