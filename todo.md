# AI Instructions
You are an AI assistant helping to complete this project.
Below is the remaining todo list for the project containing all the uncompleted parts and their details.
Please strictly follow these instructions:
1. Read the details of the tasks and start working on them one by one, in order.
2. Write the necessary code and perform the required changes for the current task.
3. When you completely finish a task or checklist item, edit this `todo.md` file to mark it as done by changing `[ ]` to `[x]`.
4. Then, move on to the next task and repeat the process until all tasks are completed.

---
## PART 8: Shifts System

### 🎯 Goal
Manage work shifts with start/end and reporting.

---

### 📋 Tasks

#### 8.1 Shift Start (Already in PART 4)

Verify implementation from Part 4 is complete.

---

#### 8.2 Create `ui/components/shift_dialog.py`

**Start Shift Dialog:** (from PART 4)

**End Shift Dialog:**

```
┌──────────────────────────────────┐
│  إنهاء الشفت                     │
├──────────────────────────────────┤
│  الشفت: صباحي                    │
│  الموظف: أحمد محمد               │
│  بدأ الساعة: 08:00 ص             │
│  ──────────────────────────────  │
│  📊 ملخص الشفت:                  │
│                                  │
│  إجمالي المبيعات: 2,500.00 ج.م  │
│  عدد الأوردرات: 45               │
│  متوسط الأوردر: 55.56 ج.م        │
│  كاش محصل: 2,500.00 ج.م          │
│  ──────────────────────────────  │
│  [ طباعة التقرير ]               │
│  [ إنهاء الشفت ]    [ إلغاء ]    │
└──────────────────────────────────┘
```

**Calculate Shift Totals:**

```python
def calculate_shift_totals(self, shift_id):
    """Calculate totals for shift"""
    
    totals = self.db.fetch_one(
        """SELECT 
           COUNT(*) as total_orders,
           SUM(total) as total_sales,
           SUM(CASE WHEN payment_method='cash' THEN total ELSE 0 END) as cash_collected
           FROM orders 
           WHERE shift_id = ? AND status = 'completed'""",
        (shift_id,)
    )
    
    return totals
```

---

#### 8.3 Create `ui/shifts_window.py`

**View all shifts:**

```
┌────────────────────────────────────────────────────────────────┐
│  الشفتات                                                       │
├────────────────────────────────────────────────────────────────┤
│  من: [____] إلى: [____]  [ عرض ]                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ التاريخ │ الشفت │ الموظف │ المبيعات │ الأوردرات │      │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 2024/01/15 │ صباحي │ أحمد │ 2,500 │ 45 │ 📄 │       │ │
│  │ 2024/01/15 │ مسائي │ محمد │ 3,200 │ 52 │ 📄 │       │ │
│  │ 2024/01/14 │ صباحي │ أحمد │ 1,800 │ 38 │ 📄 │       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  [ عرض التفاصيل ]  [ طباعة ]                                  │
└────────────────────────────────────────────────────────────────┘
```

**Features:**
- List all completed shifts
- Filter by date range
- View shift details (click 📄)
- Print shift report

---

#### 8.4 Shift Details Dialog

```
┌──────────────────────────────────┐
│  تفاصيل الشفت                    │
├──────────────────────────────────┤
│  التاريخ: 2024/01/15             │
│  الشفت: صباحي                    │
│  الموظف: أحمد محمد               │
│  من: 08:00 ص إلى: 02:30 م        │
│  المدة: 6 ساعات و 30 دقيقة       │
│  ──────────────────────────────  │
│  إجمالي المبيعات: 2,500.00 ج.م  │
│  عدد الأوردرات: 45               │
│  متوسط الأوردر: 55.56 ج.م        │
│  كاش محصل: 2,500.00 ج.م          │
│  ──────────────────────────────  │
│  📋 الأوردرات:                   │
│  ┌────────────────────────────┐  │
│  │ ORD-...-0001    55.00 ج.م │  │
│  │ ORD-...-0002    60.00 ج.م │  │
│  │ ...                       │  │
│  └────────────────────────────┘  │
│  [ طباعة ]         [ إغلاق ]    │
└──────────────────────────────────┘
```

---

### ✅ Checklist for PART 8

- [x] Start shift dialog works
- [x] Shift created in database with is_active=1
- [x] Only one active shift per employee at a time
- [x] End shift calculates totals correctly
- [x] End shift updates database (ended_at, totals, is_active=0)
- [x] Shifts window shows all completed shifts
- [x] Date filter works
- [x] Shift details dialog displays all information
- [x] Shift duration calculated correctly
- [x] Print shift report works
- [x] Can't start shift if one already active
- [x] Can't use POS without active shift

**Test:**
- Start shift as cashier
- Make several sales
- End shift
- Verify totals match actual sales
- View shift in shifts window
- Print shift report

---

## PART 9: Returns & Refunds

### 🎯 Goal
Handle order cancellations and refunds.

---

### 📋 Tasks

#### 9.1 Create `ui/returns_window.py`

```
┌────────────────────────────────────────────────────────────────┐
│  المرتجعات                                                     │
├────────────────────────────────────────────────────────────────┤
│  رقم الأوردر: [___________]  [ بحث ]                          │
│  ──────────────────────────────────────────────────────────    │
│  📋 الأوردر: ORD-20240115-0023                                │
│  التاريخ: 2024/01/15  02:15 م                                 │
│  الإجمالي: 110.00 ج.م                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ الصنف       │ الكمية │ السعر │ الإجمالي │ استرجاع │     │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ كريب جبنة   │ 2     │ 20    │ 40.00   │ ☑       │     │ │
│  │ بيتزا مارجر │ 1     │ 60    │ 60.00   │ ☑       │     │ │
│  │ كولا        │ 1     │ 10    │ 10.00   │ ☐       │     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ⚫ استرجاع كامل                                               │
│  ⚪ استرجاع جزئي                                               │
│                                                                │
│  المبلغ المسترجع: 100.00 ج.م                                  │
│  السبب (اختياري): [_____________________]                    │
│                                                                │
│  [ تأكيد الاسترجاع ]              [ إلغاء ]                   │
└────────────────────────────────────────────────────────────────┘
```

---

#### 9.2 Search Order

```python
def search_order(self, order_number):
    """Search for order by number"""
    
    order = self.db.fetch_one(
        "SELECT * FROM orders WHERE order_number = ? AND status = 'completed'",
        (order_number,)
    )
    
    if not order:
        # Show error: order not found or already returned
        return None
    
    # Load order items
    items = self.db.fetch_all(
        """SELECT oi.*, i.name 
           FROM order_items oi 
           JOIN items i ON oi.item_id = i.id 
           WHERE oi.order_id = ?""",
        (order['id'],)
    )
    
    return order, items
```

---

#### 9.3 Process Return

```python
def process_return(self, order_id, return_type, selected_items, reason):
    """Process return/refund"""
    
    # Calculate refund amount
    if return_type == 'full':
        amount = order['total']
        items_to_return = all_items
    else:  # partial
        amount = sum(item['subtotal'] for item in selected_items)
        items_to_return = selected_items
    
    # Insert return record
    employee_id = self.auth.get_current_user()['id']
    
    self.db.execute_query(
        """INSERT INTO returns (order_id, employee_id, return_type, amount, reason)
           VALUES (?, ?, ?, ?, ?)""",
        (order_id, employee_id, return_type, amount, reason)
    )
    
    # Update order status
    if return_type == 'full':
        self.db.execute_query(
            "UPDATE orders SET status = 'returned' WHERE id = ?",
            (order_id,)
        )
    
    # Return inventory
    self.return_inventory(items_to_return)
    
    # Show success message
    self.show_success(f"تم استرجاع {amount:.2f} ج.م بنجاح")
```

---

#### 9.4 Return Inventory

```python
def return_inventory(self, items):
    """Return inventory quantities"""
    
    for item in items:
        # Get recipes
        recipes = self.db.fetch_all(
            "SELECT inventory_id, quantity FROM recipes WHERE item_id = ?",
            (item['item_id'],)
        )
        
        for recipe in recipes:
            # Calculate return quantity
            return_qty = recipe['quantity'] * item['quantity']
            
            # Add back to inventory
            self.db.execute_query(
                "UPDATE inventory SET current_quantity = current_quantity + ? WHERE id = ?",
                (return_qty, recipe['inventory_id'])
            )
```

---

#### 9.5 Returns History

**Add tab to show all returns:**

```
┌────────────────────────────────────────────────────────────────┐
│  [ البحث ]  [ السجل ]                                          │
├────────────────────────────────────────────────────────────────┤
│  من: [____] إلى: [____]  [ عرض ]                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ التاريخ │ رقم الأوردر │ النوع │ المبلغ │ الموظف │       │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 2024/01/15 │ ORD-...-0023 │ كامل │ 110 ج.م │ أحمد │    │ │
│  │ 2024/01/14 │ ORD-...-0015 │ جزئي │ 40 ج.م  │ محمد │    │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

### ✅ Checklist for PART 9

- [x] Returns window displays search interface
- [x] Can search order by order number
- [x] Order details display correctly
- [x] Can select full return
- [x] Can select partial return (select items)
- [x] Refund amount calculates correctly
- [x] Return processes and saves to database
- [x] Order status updated to 'returned' (if full)
- [x] Inventory quantities added back
- [x] Returns history shows all returns
- [x] Date filter works
- [x] Can add optional reason
- [x] Success message displays
- [x] Cannot return already returned order

**Test:**
- Create order from POS
- Search for order in returns
- Process full return
- Verify inventory added back
- Verify return in database
- Check returns history

---

## PART 10: Reports & Export

### 🎯 Goal
Generate reports and export to PDF/Excel.

---

### 📋 Tasks

#### 10.1 Create `ui/reports_window.py`

**Layout:** As shown in Section 5.2.6

**Report Types:**
- يومي (Daily)
- أسبوعي (Weekly)
- شهري (Monthly)
- مخصص (Custom date range)

---

#### 10.2 Sales Report

```python
def generate_sales_report(self, start_date, end_date):
    """Generate sales report for date range"""
    
    # Total sales
    totals = self.db.fetch_one(
        """SELECT 
           COUNT(*) as total_orders,
           SUM(total) as total_sales,
           AVG(total) as avg_order,
           SUM(CASE WHEN payment_method='cash' THEN total ELSE 0 END) as cash_total
           FROM orders 
           WHERE DATE(created_at) BETWEEN ? AND ? 
           AND status = 'completed'""",
        (start_date, end_date)
    )
    
    # Top selling items
    top_items = self.db.fetch_all(
        """SELECT i.name, SUM(oi.quantity) as qty, SUM(oi.subtotal) as total
           FROM order_items oi
           JOIN items i ON oi.item_id = i.id
           JOIN orders o ON oi.order_id = o.id
           WHERE DATE(o.created_at) BETWEEN ? AND ?
           AND o.status = 'completed'
           GROUP BY i.id
           ORDER BY qty DESC
           LIMIT 10""",
        (start_date, end_date)
    )
    
    # Sales by category
    category_sales = self.db.fetch_all(
        """SELECT c.name, SUM(oi.subtotal) as total
           FROM order_items oi
           JOIN items i ON oi.item_id = i.id
           JOIN categories c ON i.category_id = c.id
           JOIN orders o ON oi.order_id = o.id
           WHERE DATE(o.created_at) BETWEEN ? AND ?
           AND o.status = 'completed'
           GROUP BY c.id""",
        (start_date, end_date)
    )
    
    return {
        'totals': totals,
        'top_items': top_items,
        'category_sales': category_sales
    }
```

---

#### 10.3 Inventory Report

```python
def generate_inventory_report(self):
    """Generate current inventory status"""
    
    items = self.db.fetch_all(
        """SELECT 
           name,
           current_quantity,
           unit,
           min_alert_quantity,
           CASE 
             WHEN current_quantity <= min_alert_quantity THEN 'منخفض'
             ELSE 'جيد'
           END as status
           FROM inventory
           ORDER BY 
             CASE WHEN current_quantity <= min_alert_quantity THEN 0 ELSE 1 END,
             name"""
    )
    
    # Low stock count
    low_stock_count = sum(1 for item in items if item['status'] == 'منخفض')
    
    return {
        'items': items,
        'low_stock_count': low_stock_count
    }
```

---

#### 10.4 PDF Export

Create `utils/pdf_generator.py`

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime

class PDFGenerator:
    def __init__(self, config):
        self.config = config
        
        # Register Arabic font
        # (You'll need to include Arabic TTF font file)
        # pdfmetrics.registerFont(TTFont('Arabic', 'fonts/arabic.ttf'))
        
    def generate_sales_report(self, report_data, filename):
        """Generate PDF sales report"""
        
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont('Arabic', 16)
        c.drawRightString(width - 20*mm, height - 20*mm, self.config.get('restaurant.name'))
        
        c.setFont('Arabic', 14)
        c.drawRightString(width - 20*mm, height - 30*mm, 'تقرير المبيعات')
        
        # Date
        c.setFont('Arabic', 10)
        date_str = datetime.now().strftime('%Y/%m/%d %I:%M %p')
        c.drawRightString(width - 20*mm, height - 40*mm, f'التاريخ: {date_str}')
        
        # Totals
        y = height - 60*mm
        c.setFont('Arabic', 12)
        
        totals = report_data['totals']
        c.drawRightString(width - 20*mm, y, f"إجمالي المبيعات: {totals['total_sales']:.2f} ج.م")
        y -= 7*mm
        c.drawRightString(width - 20*mm, y, f"عدد الأوردرات: {totals['total_orders']}")
        y -= 7*mm
        c.drawRightString(width - 20*mm, y, f"متوسط الأوردر: {totals['avg_order']:.2f} ج.م")
        
        # Top items
        y -= 15*mm
        c.setFont('Arabic', 14)
        c.drawRightString(width - 20*mm, y, 'الأصناف الأكثر مبيعاً')
        
        y -= 10*mm
        c.setFont('Arabic', 10)
        for idx, item in enumerate(report_data['top_items'], 1):
            c.drawRightString(width - 20*mm, y, f"{idx}. {item['name']} - {item['qty']} قطعة")
            y -= 6*mm
        
        c.save()
```

**Note:** For proper Arabic support in PDF, you need to:
1. Include Arabic TTF font (e.g., `assets/fonts/NotoSansArabic.ttf`)
2. Register font in reportlab
3. Use RTL text rendering

**Alternative:** Use HTML to PDF library like `weasyprint` which handles Arabic better.

---

#### 10.5 Excel Export

Create `utils/excel_generator.py`

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime

class ExcelGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_sales_report(self, report_data, filename):
        """Generate Excel sales report"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "تقرير المبيعات"
        
        # RTL
        ws.sheet_view.rightToLeft = True
        
        # Header
        ws['A1'] = self.config.get('restaurant.name')
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].alignment = Alignment(horizontal='right')
        
        ws['A2'] = 'تقرير المبيعات'
        ws['A2'].font = Font(size=14, bold=True)
        
        ws['A3'] = f"التاريخ: {datetime.now().strftime('%Y/%m/%d %I:%M %p')}"
        
        # Totals
        row = 5
        totals = report_data['totals']
        
        ws[f'A{row}'] = 'إجمالي المبيعات'
        ws[f'B{row}'] = f"{totals['total_sales']:.2f} ج.م"
        row += 1
        
        ws[f'A{row}'] = 'عدد الأوردرات'
        ws[f'B{row}'] = totals['total_orders']
        row += 1
        
        ws[f'A{row}'] = 'متوسط الأوردر'
        ws[f'B{row}'] = f"{totals['avg_order']:.2f} ج.م"
        row += 2
        
        # Top items
        ws[f'A{row}'] = 'الأصناف الأكثر مبيعاً'
        ws[f'A{row}'].font = Font(bold=True)
        row += 1
        
        ws[f'A{row}'] = 'الصنف'
        ws[f'B{row}'] = 'الكمية'
        ws[f'C{row}'] = 'الإجمالي'
        
        # Header style
        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = Font(bold=True)
            ws[f'{col}{row}'].fill = PatternFill(start_color='CCCCCC', fill_type='solid')
        
        row += 1
        
        for item in report_data['top_items']:
            ws[f'A{row}'] = item['name']
            ws[f'B{row}'] = item['qty']
            ws[f'C{row}'] = f"{item['total']:.2f}"
            row += 1
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        
        wb.save(filename)
```

---

#### 10.6 Export Buttons

```python
def export_pdf(self):
    """Export current report as PDF"""
    from utils.pdf_generator import PDFGenerator
    
    # Get report data
    report_data = self.current_report_data
    
    # Generate filename
    filename = f"exports/pdf/sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Generate PDF
    pdf = PDFGenerator(self.config)
    pdf.generate_sales_report(report_data, filename)
    
    # Show success
    self.show_success(f"تم حفظ التقرير في: {filename}")

def export_excel(self):
    """Export current report as Excel"""
    from utils.excel_generator import ExcelGenerator
    
    # Similar to PDF export
```

---

### ✅ Checklist for PART 10

- [x] Reports window displays with date range selector
- [x] Report types dropdown works
- [x] Sales report generates correctly
- [x] Totals calculate correctly
- [x] Top selling items display
- [x] Category sales breakdown works
- [x] Inventory report shows current stock
- [x] Low stock items highlighted
- [x] PDF export works
- [x] PDF has correct Arabic text
- [x] Excel export works
- [x] Excel RTL layout works
- [x] Files saved to exports folder
- [x] Success message shows file path
- [x] Cashier can view reports
- [x] Manager can view all reports

**Test:**
- Generate daily report
- Verify totals match database
- Export to PDF
- Export to Excel
- Open files and verify content
- Generate inventory report
- Verify low stock items shown

---

## PART 11: Settings Screen

### 🎯 Goal
Manage application settings (manager only).

---

### 📋 Tasks

#### 11.1 Create `ui/settings_window.py`

```
┌────────────────────────────────────────────────────────────────┐
│  الإعدادات                                                     │
├────────────────────────────────────────────────────────────────┤
│  [ المطعم ]  [ النظام ]  [ النسخ الاحتياطي ]                  │
├────────────────────────────────────────────────────────────────┤
│  📋 بيانات المطعم                                              │
│  ─────────────────────────────────────────────────────────     │
│  اسم المطعم: [________________________]                       │
│  العنوان: [________________________]                          │
│  التليفون: [________________________]                         │
│  ─────────────────────────────────────────────────────────     │
│  ⚙️ إعدادات النظام                                             │
│  ─────────────────────────────────────────────────────────     │
│  ☑ تفعيل الطاولات                                             │
│  ☑ تفعيل الطابعة                                              │
│  ─────────────────────────────────────────────────────────     │
│  رسالة الشكر: [________________________]                      │
│  ─────────────────────────────────────────────────────────     │
│  [ حفظ التغييرات ]                                            │
└────────────────────────────────────────────────────────────────┘
```

---

#### 11.2 Read-Only Restaurant Info

**Important:** Restaurant name, address, phone are READ-ONLY in the app.

Show message: "لتغيير هذه البيانات، تواصل مع مطور البرنامج"

Only developer can change these via `setup_restaurant.py`

---

#### 11.3 Editable Settings

Settings stored in database `settings` table:

- `tables_enabled`: Can be toggled by manager
- `printer_enabled`: Can be toggled by manager
- `thank_you_message`: Can be edited by manager

```python
def save_settings(self):
    """Save settings to database"""
    
    self.db.execute_query(
        "UPDATE settings SET value = ? WHERE key = 'tables_enabled'",
        ('1' if self.tables_checkbox.isChecked() else '0',)
    )
    
    self.db.execute_query(
        "UPDATE settings SET value = ? WHERE key = 'printer_enabled'",
        ('1' if self.printer_checkbox.isChecked() else '0',)
    )
    
    self.db.execute_query(
        "UPDATE settings SET value = ? WHERE key = 'thank_you_message'",
        (self.thank_you_input.text(),)
    )
    
    self.show_success("تم حفظ الإعدادات بنجاح")
```

---

#### 11.4 Backup & Restore

Create `utils/backup.py`

```python
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> str:
        """Create database backup"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"restaurant_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        # Copy database file
        shutil.copy(self.db_path, backup_path)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str):
        """Restore database from backup"""
        
        # Close current database connection first!
        
        # Copy backup over current database
        shutil.copy(backup_path, self.db_path)
        
        # Reconnect database
```

**Settings Tab for Backup:**

```
┌────────────────────────────────────────────────────────────────┐
│  💾 النسخ الاحتياطي                                            │
│  ─────────────────────────────────────────────────────────     │
│  [ إنشاء نسخة احتياطية ]                                      │
│  ─────────────────────────────────────────────────────────     │
│  📂 النسخ الاحتياطية المتوفرة:                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ restaurant_backup_20240115_143022.db  [استرجاع] [حذف]   │ │
│  │ restaurant_backup_20240114_091530.db  [استرجاع] [حذف]   │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

### ✅ Checklist for PART 11

- [x] Settings window displays all tabs
- [x] Restaurant info shown (read-only)
- [x] Tables enabled checkbox works
- [x] Printer enabled checkbox works
- [x] Thank you message editable
- [x] Save button updates database
- [x] Success message displays
- [x] Create backup works
- [x] Backup file created in backups folder
- [x] List of backups displays
- [x] Restore backup works
- [x] Warning shown before restore
- [x] Delete backup works
- [x] Only managers can access settings

**Test:**
- Toggle tables setting
- Save and verify in database
- Create backup
- Make some changes
- Restore backup
- Verify changes reverted

---

## PART 12: Printer Support

### 🎯 Goal
Add thermal printer support for invoices.

---

### 📋 Tasks

#### 12.1 Create `utils/printer.py`

**For Windows Thermal Printer (80mm):**

```python
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont

class ThermalPrinter:
    def __init__(self, printer_name=None):
        """
        Initialize printer
        If printer_name is None, use default printer
        """
        if printer_name:
            self.printer_name = printer_name
        else:
            self.printer_name = win32print.GetDefaultPrinter()
    
    def print_invoice(self, invoice_data):
        """Print invoice to thermal printer"""
        
        # Create invoice image
        img = self.create_invoice_image(invoice_data)
        
        # Print image
        self.print_image(img)
    
    def create_invoice_image(self, invoice_data):
        """Create invoice as image (80mm = ~300px width)"""
        
        # 80mm = 302 pixels at 96 DPI
        width = 300
        
        # Calculate height based on content
        height = 400  # Will adjust dynamically
        
        # Create image
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Load Arabic font
        try:
            font_regular = ImageFont.truetype('assets/fonts/NotoSansArabic-Regular.ttf', 14)
            font_bold = ImageFont.truetype('assets/fonts/NotoSansArabic-Bold.ttf', 16)
            font_small = ImageFont.truetype('assets/fonts/NotoSansArabic-Regular.ttf', 10)
        except:
            font_regular = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        y = 10
        
        # Restaurant name (centered)
        text = invoice_data['restaurant_name']
        bbox = draw.textbbox((0, 0), text, font=font_bold)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font_bold, fill='black')
        y += 25
        
        # Address & phone
        text = invoice_data['restaurant_address']
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font_small, fill='black')
        y += 15
        
        text = invoice_data['restaurant_phone']
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font_small, fill='black')
        y += 20
        
        # Line
        draw.line([(10, y), (width-10, y)], fill='black', width=1)
        y += 10
        
        # Order number, date, time
        draw.text((width-10, y), f"رقم الأوردر: {invoice_data['order_number']}", 
                  font=font_small, fill='black', anchor='ra')
        y += 15
        
        draw.text((width-10, y), f"التاريخ: {invoice_data['date']}", 
                  font=font_small, fill='black', anchor='ra')
        y += 15
        
        draw.text((width-10, y), f"الوقت: {invoice_data['time']}", 
                  font=font_small, fill='black', anchor='ra')
        y += 20
        
        # Line
        draw.line([(10, y), (width-10, y)], fill='black', width=1)
        y += 10
        
        # Items
        for item in invoice_data['items']:
            text = f"{item['name']}  x{item['quantity']}"
            draw.text((width-10, y), text, font=font_regular, fill='black', anchor='ra')
            
            price_text = f"{item['subtotal']:.2f}"
            draw.text((10, y), price_text, font=font_regular, fill='black')
            y += 20
        
        # Line
        draw.line([(10, y), (width-10, y)], fill='black', width=1)
        y += 10
        
        # Total
        draw.text((width-10, y), "الإجمالي:", font=font_bold, fill='black', anchor='ra')
        draw.text((10, y), f"{invoice_data['total']:.2f} ج.م", 
                  font=font_bold, fill='black')
        y += 25
        
        # Thank you message
        text = invoice_data['thank_you_message']
        bbox = draw.textbbox((0, 0), text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font_small, fill='black')
        y += 20
        
        # Crop image to actual height
        img = img.crop((0, 0, width, y))
        
        return img
    
    def print_image(self, img):
        """Send image to printer"""
        
        hprinter = win32print.OpenPrinter(self.printer_name)
        
        try:
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(self.printer_name)
            hdc.StartDoc('Invoice')
            hdc.StartPage()
            
            # Convert PIL image to bitmap and print
            dib = ImageWin.Dib(img)
            dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
            
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        finally:
            win32print.ClosePrinter(hprinter)
    
    @staticmethod
    def get_available_printers():
        """Get list of available printers"""
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printers.append(printer[2])
        return printers
```

**Required packages:**
```
pywin32
Pillow
```

---

#### 12.2 Integrate Printer in Invoice Dialog

```python
def print_invoice(self):
    """Print invoice"""
    
    # Check if printer enabled
    printer_enabled = self.db.fetch_one(
        "SELECT value FROM settings WHERE key = 'printer_enabled'"
    )
    
    if not printer_enabled or printer_enabled['value'] == '0':
        # Show print preview instead
        self.show_print_preview()
        return
    
    try:
        from utils.printer import ThermalPrinter
        
        # Prepare invoice data
        invoice_data = {
            'restaurant_name': self.config.get('restaurant.name'),
            'restaurant_address': self.config.get('restaurant.address'),
            'restaurant_phone': self.config.get('restaurant.phone'),
            'order_number': self.order['order_number'],
            'date': self.order['date'],
            'time': self.order['time'],
            'items': self.order_items,
            'total': self.order['total'],
            'thank_you_message': self.config.get('invoice.thank_you_message')
        }
        
        # Print
        printer = ThermalPrinter()
        printer.print_invoice(invoice_data)
        
        self.show_success("تم الطباعة بنجاح")
        
    except Exception as e:
        self.show_error(f"خطأ في الطباعة: {str(e)}")
```

---

#### 12.3 Printer Settings

Add to settings window:

```
┌────────────────────────────────────────────────────────────────┐
│  🖨️ إعدادات الطابعة                                            │
│  ─────────────────────────────────────────────────────────     │
│  ☑ تفعيل الطابعة                                              │
│  ─────────────────────────────────────────────────────────     │
│  اختر الطابعة:                                                │
│  [▼ POS-80 Thermal Printer               ]                    │
│  ─────────────────────────────────────────────────────────     │
│  [ اختبار الطباعة ]                                           │
└────────────────────────────────────────────────────────────────┘
```

Load printers list:
```python
from utils.printer import ThermalPrinter

printers = ThermalPrinter.get_available_printers()
self.printer_combo.addItems(printers)
```

---

### ✅ Checklist for PART 12

- [x] Printer utility created
- [x] Can get list of available printers
- [x] Invoice image generation works
- [x] Arabic text renders correctly in image
- [x] Print to thermal printer works
- [x] Invoice formatted correctly (80mm width)
- [x] Print button in invoice dialog works
- [x] Settings has printer selection
- [x] Test print works
- [x] Graceful fallback if no printer
- [x] Error handling for print failures

**Test:**
- Connect thermal printer (or use PDF printer for testing)
- Enable printer in settings
- Select printer
- Make sale and print invoice
- Verify invoice printed correctly
- Test with printer disabled (should show preview)

---

## HOW TO USE THIS FILE

### For AI (Claude, ChatGPT, etc.)

**When starting a new chat:**

1. Upload this entire file
2. Tell AI: "Read this specification file. I want to implement PART X. Follow the specifications exactly."
3. AI will have full context of the project

**When continuing:**

1. Upload this file again (or reference it if in same chat)
2. Say: "Continue from PART X. Here's what's done: [list completed items from checklist]"

**When debugging:**

1. Reference specific section: "Check PART 6, section 6.4 - the inventory deduction isn't working"
2. AI has full context to help

---

### For Developer

**Implementation Order:**

✅ Recommended sequence (some parts can be parallel):

```
PART 1 → PART 2 → PART 3 → PART 4 → PART 5 → PART 6 → PART 7 → PART 8 → PART 9 → PART 10 → PART 11 → PART 12
```

**Testing Strategy:**

- Complete each part fully before moving to next
- Run checklist after each part
- Keep test data (sample categories, items, etc.)
- Test with real scenarios

**Customization for Each Restaurant:**

1. Run `python setup_restaurant.py`
2. Enter restaurant details
3. Copy `config.encrypted` and `config.key` to installation
4. Replace `assets/logo.png`
5. Install on client machine
6. First run creates database
7. Set up initial categories and menu items
8. Add employees
9. Train staff

---

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --name="RestaurantPOS" \
            --windowed \
            --onefile \
            --icon=assets/icon.ico \
            --add-data="assets;assets" \
            --add-data="config.encrypted;." \
            --add-data="database/schema.sql;database" \
            main.py

# Output: dist/RestaurantPOS.exe
```

**Distribute:**
- Copy `dist/RestaurantPOS.exe`
- Copy `config.encrypted` (customized for restaurant)
- Copy `assets` folder
- Create `database`, `exports`, `backups` folders

---

### Maintenance

**Adding New Feature:**
1. Update this file with new section
2. Implement
3. Update checklist

**Bug Fix:**
1. Note issue in relevant section
2. Fix
3. Update specifications if needed

---

### Notes

- **Security:** Keep `config.key` secure. Without it, `config.encrypted` cannot be read.
- **Backup:** Always backup before major changes.
- **Testing:** Test thoroughly with each restaurant before deployment.
- **Updates:** For updates, replace .exe but keep database and config files.

---

## END OF SPECIFICATION

**Total Parts:** 12
**Estimated Development Time:** 40-60 hours
**Lines of Code:** ~5,000-7,000

This specification is complete and ready for AI implementation. Start with PART 1 and follow sequentially.

