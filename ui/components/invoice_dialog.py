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

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.text.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.text.setHtml(self.format_invoice_html())
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        print_btn = QPushButton("طباعة الفاتورة")
        print_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px;")
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.clicked.connect(self.print_direct)
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def format_invoice_html(self):
        """Build a clean HTML invoice with a proper table layout."""
        order_num = self.order.get('order_number', '')
        order_time = self.order.get('order_time', '')

        rows_html = ""
        total = 0
        for i, it in enumerate(self.items):
            name = it.get('name', '')
            qty = it.get('quantity', 0)
            price = it.get('price_at_time', 0)
            subtotal = qty * price
            total += subtotal
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            rows_html += f"""
            <tr style="background: {bg};">
                <td style="padding: 6px 10px; text-align: right; font-size: 13px;">{name}</td>
                <td style="padding: 6px 10px; text-align: center; font-size: 13px;">{qty}</td>
                <td style="padding: 6px 10px; text-align: center; font-size: 13px;">{price:.2f}</td>
                <td style="padding: 6px 10px; text-align: center; font-size: 13px; font-weight: bold;">{subtotal:.2f}</td>
            </tr>"""

        html = f"""
        <div style="direction: rtl; font-family: 'Segoe UI', Tahoma, sans-serif;">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 4px;">فاتورة</h2>
            <p style="text-align: center; color: #7f8c8d; font-size: 12px; margin: 2px 0;">
                رقم الطلب: <b>{order_num}</b>
            </p>
            <p style="text-align: center; color: #7f8c8d; font-size: 12px; margin: 2px 0 10px 0;">
                التاريخ: {order_time}
            </p>
            <hr style="border: 1px solid #bdc3c7;">
            <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse: collapse; margin-top: 6px;">
                <thead>
                    <tr style="background: #2c3e50; color: white;">
                        <th style="padding: 8px 10px; text-align: right; font-size: 13px;">الصنف</th>
                        <th style="padding: 8px 10px; text-align: center; font-size: 13px;">الكمية</th>
                        <th style="padding: 8px 10px; text-align: center; font-size: 13px;">السعر</th>
                        <th style="padding: 8px 10px; text-align: center; font-size: 13px;">الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <hr style="border: 1px solid #bdc3c7; margin-top: 8px;">
            <h3 style="text-align: center; color: #27ae60; margin: 10px 0 4px 0;">
                الإجمالي: {total:.2f} ج.م
            </h3>
            <p style="text-align: center; color: #95a5a6; font-size: 12px; margin-top: 12px;">
                شكراً لزيارتكم 🙏
            </p>
        </div>
        """
        return html

    def format_invoice_text(self):
        """Plain-text version for file saving."""
        lines = []
        lines.append(f"رقم الطلب: {self.order.get('order_number','')}")
        lines.append(f"التاريخ: {self.order.get('order_time','')}")
        lines.append("=" * 40)
        lines.append(f"{'الصنف':<18} {'الكمية':>4}  {'السعر':>8}  {'الإجمالي':>8}")
        lines.append("-" * 40)
        total = 0
        for it in self.items:
            name = it.get('name', '')
            qty = it.get('quantity', 0)
            price = it.get('price_at_time', 0)
            subtotal = qty * price
            total += subtotal
            lines.append(f"{name:<18} {qty:>4}  {price:>8.2f}  {subtotal:>8.2f}")
        lines.append("=" * 40)
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
