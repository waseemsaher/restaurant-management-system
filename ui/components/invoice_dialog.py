from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import os
from datetime import datetime
import subprocess
from utils.config import ConfigManager

class InvoiceDialog(QDialog):
    def __init__(self, parent, order: dict, items: list):
        super().__init__(parent)
        self.order = order
        self.items = items
        self.setWindowTitle("فاتورة")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(420, 480)
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
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_to_file)
        print_btn = QPushButton("طباعة")
        print_btn.clicked.connect(self.print_direct)
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(save_btn)
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
        # Try to save then send to system print command (lp or lpr)
        filename = self.save_to_file()
        if not filename:
            return
        # try lp then lpr
        for cmd in ("lp", "lpr"):
            try:
                subprocess.run([cmd, filename], check=True)
                QMessageBox.information(self, "طباعة", "تم إرسال الفاتورة إلى الطابعة.")
                return
            except FileNotFoundError:
                continue
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "طباعة", f"فشل الطباعة: {e}")
                return
        QMessageBox.information(self, "طباعة", "لم يتم العثور على أوامر الطباعة (lp/lpr). يمكنك طباعة الملف يدوياً.")
