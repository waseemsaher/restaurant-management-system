import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QGroupBox, QComboBox, QDateEdit, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from database.db import Database
from datetime import datetime
from utils.pdf_generator import PDFGenerator
from utils.excel_generator import ExcelGenerator

class ReportsScreen(QWidget):
    def __init__(self, user_session: dict):
        super().__init__()
        self.user_session = user_session
        self.db = Database()
        self.current_report_data = None
        self.init_ui()
        self.load_report()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.tabs = QTabWidget()
        
        # Sales Tab
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        sales_layout.setContentsMargins(4, 4, 4, 4)
        sales_layout.setSpacing(4)
        
        # Date filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("نوع التقرير:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["يومي", "أسبوعي", "شهري", "مخصص"])
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        filter_layout.addWidget(self.report_type_combo)
        
        filter_layout.addWidget(QLabel("من:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        btn_show = QPushButton("عرض")
        btn_show.clicked.connect(self.load_report)
        filter_layout.addWidget(btn_show)
        filter_layout.addStretch()
        
        sales_layout.addLayout(filter_layout)
        
        # Summary
        summary_group = QGroupBox("📊 ملخص المبيعات")
        summary_layout_box = QHBoxLayout(summary_group)
        summary_layout_box.setContentsMargins(6, 4, 6, 4)
        self.sales_total_lbl = QLabel("إجمالي المبيعات: 0.00 ج.م")
        self.sales_total_lbl.setStyleSheet("font-weight: bold;")
        self.orders_count_lbl = QLabel("عدد الأوردرات: 0")
        self.avg_order_lbl = QLabel("متوسط الأوردر: 0.00 ج.م")
        summary_layout_box.addWidget(self.sales_total_lbl)
        summary_layout_box.addWidget(self.orders_count_lbl)
        summary_layout_box.addWidget(self.avg_order_lbl)
        sales_layout.addWidget(summary_group)
        
        # Top items & Categories
        split_layout = QHBoxLayout()
        
        top_group = QGroupBox("📈 الأصناف الأكثر مبيعاً")
        top_layout = QVBoxLayout(top_group)
        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(3)
        self.top_items_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
        self.top_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        top_layout.addWidget(self.top_items_table)
        split_layout.addWidget(top_group)
        
        cat_group = QGroupBox("مبيعات الأقسام")
        cat_layout = QVBoxLayout(cat_group)
        self.cat_sales_table = QTableWidget()
        self.cat_sales_table.setColumnCount(2)
        self.cat_sales_table.setHorizontalHeaderLabels(["القسم", "الإجمالي"])
        self.cat_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cat_sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cat_layout.addWidget(self.cat_sales_table)
        split_layout.addWidget(cat_group)
        
        sales_layout.addLayout(split_layout)
        
        # Export buttons
        export_layout = QHBoxLayout()
        btn_pdf = QPushButton("تصدير PDF")
        btn_pdf.clicked.connect(self.export_pdf)
        btn_excel = QPushButton("تصدير Excel")
        btn_excel.clicked.connect(self.export_excel)
        export_layout.addWidget(btn_pdf)
        export_layout.addWidget(btn_excel)
        export_layout.addStretch()
        sales_layout.addLayout(export_layout)
        
        self.tabs.addTab(sales_tab, "المبيعات")
        
        # Inventory Tab
        inv_tab = QWidget()
        inv_layout = QVBoxLayout(inv_tab)
        inv_layout.setContentsMargins(4, 4, 4, 4)
        inv_layout.setSpacing(4)
        
        inv_summary = QGroupBox("موقف المخزون")
        inv_sum_layout = QVBoxLayout(inv_summary)
        self.low_stock_lbl = QLabel("أصناف منخفضة الرصيد: 0")
        self.low_stock_lbl.setStyleSheet("color: red; font-weight: bold;")
        inv_sum_layout.addWidget(self.low_stock_lbl)
        inv_layout.addWidget(inv_summary)
        
        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(5)
        self.inv_table.setHorizontalHeaderLabels(["المادة", "الرصيد الحالي", "الوحدة", "الحد الأدنى", "الحالة"])
        self.inv_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inv_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        inv_layout.addWidget(self.inv_table)
        
        btn_refresh_inv = QPushButton("تحديث")
        btn_refresh_inv.clicked.connect(self.load_inventory_report)
        inv_layout.addWidget(btn_refresh_inv)
        
        self.tabs.addTab(inv_tab, "المخزون")
        
        main_layout.addWidget(self.tabs)
        self.on_report_type_changed()

    def on_report_type_changed(self):
        rt = self.report_type_combo.currentText()
        today = QDate.currentDate()
        if rt == "يومي":
            self.date_from.setDate(today)
            self.date_to.setDate(today)
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
        elif rt == "أسبوعي":
            self.date_from.setDate(today.addDays(-7))
            self.date_to.setDate(today)
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
        elif rt == "شهري":
            self.date_from.setDate(today.addDays(-30))
            self.date_to.setDate(today)
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)
        else:
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)

    def load_report(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        d_to = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"
        
        totals = self.db.execute(
            """SELECT 
               COUNT(*) as total_orders,
               SUM(total_amount) as total_sales,
               AVG(total_amount) as avg_order,
               SUM(CASE WHEN payment_method='cash' THEN total_amount ELSE 0 END) as cash_total
               FROM orders 
               WHERE order_time BETWEEN ? AND ? 
               AND is_returned = 0""",
            (d_from, d_to)
        )
        
        top_items = self.db.execute(
            """SELECT i.name, SUM(oi.quantity) as qty, SUM(oi.price_at_time * oi.quantity) as total
               FROM order_items oi
               JOIN menu_items i ON oi.menu_item_id = i.id
               JOIN orders o ON oi.order_id = o.id
               WHERE o.order_time BETWEEN ? AND ?
               AND o.is_returned = 0
               GROUP BY i.id
               ORDER BY qty DESC
               LIMIT 10""",
            (d_from, d_to)
        )
        
        category_sales = self.db.execute(
            """SELECT c.name, SUM(oi.price_at_time * oi.quantity) as total
               FROM order_items oi
               JOIN menu_items i ON oi.menu_item_id = i.id
               JOIN menu_categories c ON i.category_id = c.id
               JOIN orders o ON oi.order_id = o.id
               WHERE o.order_time BETWEEN ? AND ?
               AND o.is_returned = 0
               GROUP BY c.id""",
            (d_from, d_to)
        )
        
        if totals and totals[0]['total_orders'] > 0:
            t = totals[0]
            ts = t['total_sales'] or 0.0
            avg = t['avg_order'] or 0.0
            self.sales_total_lbl.setText(f"إجمالي المبيعات: {ts:.2f} ج.م")
            self.orders_count_lbl.setText(f"عدد الأوردرات: {t['total_orders']}")
            self.avg_order_lbl.setText(f"متوسط الأوردر: {avg:.2f} ج.م")
        else:
            self.sales_total_lbl.setText("إجمالي المبيعات: 0.00 ج.م")
            self.orders_count_lbl.setText("عدد الأوردرات: 0")
            self.avg_order_lbl.setText("متوسط الأوردر: 0.00 ج.م")
            
        self.top_items_table.setRowCount(len(top_items))
        for i, item in enumerate(top_items):
            self.top_items_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.top_items_table.setItem(i, 1, QTableWidgetItem(str(item['qty'])))
            self.top_items_table.setItem(i, 2, QTableWidgetItem(f"{item['total']:.2f}"))
            
        self.cat_sales_table.setRowCount(len(category_sales))
        for i, cat in enumerate(category_sales):
            self.cat_sales_table.setItem(i, 0, QTableWidgetItem(cat['name']))
            self.cat_sales_table.setItem(i, 1, QTableWidgetItem(f"{cat['total']:.2f}"))
            
        self.current_report_data = {
            'totals': totals[0] if totals else {},
            'top_items': top_items,
            'category_sales': category_sales
        }
        
        self.load_inventory_report()

    def load_inventory_report(self):
        items = self.db.execute(
            """SELECT 
               name,
               current_quantity,
               unit,
               min_quantity,
               CASE 
                 WHEN current_quantity <= min_quantity THEN 'منخفض'
                 ELSE 'جيد'
               END as status
               FROM inventory_items
               ORDER BY 
                 CASE WHEN current_quantity <= min_quantity THEN 0 ELSE 1 END,
                 name"""
        )
        
        low_stock_count = sum(1 for item in items if item['status'] == 'منخفض')
        self.low_stock_lbl.setText(f"أصناف منخفضة الرصيد: {low_stock_count}")
        
        self.inv_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.inv_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.inv_table.setItem(i, 1, QTableWidgetItem(str(item['current_quantity'])))
            self.inv_table.setItem(i, 2, QTableWidgetItem(item['unit']))
            self.inv_table.setItem(i, 3, QTableWidgetItem(str(item['min_quantity'])))
            status_item = QTableWidgetItem(item['status'])
            if item['status'] == 'منخفض':
                status_item.setForeground(Qt.GlobalColor.red)
            self.inv_table.setItem(i, 4, status_item)

    def export_pdf(self):
        if not self.current_report_data: return
        filename = f"exports/pdf/sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = PDFGenerator({})
        try:
            pdf.generate_sales_report(self.current_report_data, filename)
            QMessageBox.information(self, "نجاح", f"تم حفظ التقرير في: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل التصدير: {e}")

    def export_excel(self):
        if not self.current_report_data: return
        filename = f"exports/excel/sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel = ExcelGenerator({})
        try:
            excel.generate_sales_report(self.current_report_data, filename)
            QMessageBox.information(self, "نجاح", f"تم حفظ التقرير في: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل التصدير: {e}")
