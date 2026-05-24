# 🚀 هبدأ أكتب الملف دلوقتي

---

```markdown
# RESTAURANT MANAGEMENT SYSTEM - COMPLETE SPECIFICATION

---
**ملاحظات تنفيذية مهمة قبل البدء:**

1. **ابدأ من PART 1 فقط**، وبعد كل جزء حدّث checklist داخل الملف عشان يوضح الصورة كاملة.
2. **Arabic PDF**: استخدم `arabic-reshaper` و `python-bidi` مع `reportlab` عشان العربية تظهر بشكل صحيح.
3. **Arabic text في PyQt6**: فعّل `QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)` من البداية، وخلّي المحاذاة لليمين في الحقول والنصوص.
4. **الطباعة**: `pywin32` خاص بـ Windows، فغلف كود الطباعة في `try/except ImportError`.
5. **requirements.txt** لازم يضم:
```
arabic-reshaper==3.0.0
python-bidi==0.4.2
```
6. **بعد إنهاء كل PART**: علّم العناصر المنجزة في checklist داخل هذا الملف فقط، واترك غير المنجز كما هو.

---
## TABLE OF CONTENTS

1. [PROJECT CONTEXT](#1-project-context)
2. [TECH STACK & DECISIONS](#2-tech-stack--decisions)
3. [DATABASE SCHEMA](#3-database-schema)
4. [PROJECT STRUCTURE](#4-project-structure)
5. [UI/UX SPECIFICATIONS](#5-uiux-specifications)
6. [PART 1: Project Setup & Database](#part-1-project-setup--database)
7. [PART 2: Configuration System](#part-2-configuration-system)
8. [PART 3: Authentication & Employees](#part-3-authentication--employees)
9. [PART 4: Main Window & Navigation](#part-4-main-window--navigation)
10. [PART 5: Menu Management](#part-5-menu-management)
11. [PART 6: POS / Cashier Screen](#part-6-pos--cashier-screen)
12. [PART 7: Inventory System](#part-7-inventory-system)
13. [PART 8: Shifts System](#part-8-shifts-system)
14. [PART 9: Returns & Refunds](#part-9-returns--refunds)
15. [PART 10: Reports & Export](#part-10-reports--export)
16. [PART 11: Settings Screen](#part-11-settings-screen)
17. [PART 12: Printer Support](#part-12-printer-support)
18. [HOW TO USE THIS FILE](#how-to-use-this-file)

---
هخلي الكلام مختصر ومباشر تضيفه في أول الملف:

---



## 1. PROJECT CONTEXT

### 1.1 Overview
Desktop application for restaurant management (primarily crepe restaurants, but customizable for pizza, burger, etc.)

### 1.2 Target Users
- **Cashier**: Takes orders, processes sales, handles returns
- **Manager**: All cashier functions + reports + inventory + employee management

### 1.3 Business Model
- Software will be SOLD to different restaurants
- Each installation will be CUSTOMIZED per restaurant
- Developer installs and customizes on-site with client

### 1.4 Key Requirements
- ✅ Offline-only (no internet required)
- ✅ Windows desktop application
- ✅ Arabic language interface
- ✅ Egyptian Pound (EGP) currency
- ✅ Easy to use for non-technical users
- ✅ Optional thermal printer support (80mm)
- ✅ Customizable per restaurant without code changes

---

## 2. TECH STACK & DECISIONS

### 2.1 Programming Language
**Python 3.11+**

### 2.2 UI Framework
**PyQt6**
- Reasons: Professional, full RTL Arabic support, rich components, easy to build .exe

### 2.3 Database
**SQLite**
- Single file database (.db)
- No server required
- Easy backup (copy file)
- Fast for single-location use

### 2.4 Additional Libraries
```python
PyQt6==6.6.0
reportlab==4.0.7        # PDF generation
openpyxl==3.1.2         # Excel export
cryptography==41.0.7    # Config encryption
Pillow==10.1.0          # Image handling
```

### 2.5 Distribution
**PyInstaller** - Create standalone .exe for Windows

---

## 3. DATABASE SCHEMA

### 3.1 Tables Overview
```
1. employees          - Staff accounts and roles
2. categories         - Menu categories (Crepes, Pizza, etc.)
3. items              - Menu items/dishes
4. inventory          - Raw materials
5. recipes            - Link items to inventory (auto deduction)
6. orders             - All orders/invoices
7. order_items        - Items in each order
8. shifts             - Work shifts
9. returns            - Returned orders/items
10. settings          - App settings
11. tables            - Restaurant tables (optional)
```

---

### 3.2 Detailed Schema

#### Table: `employees`
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('manager', 'cashier')),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields Explanation:**
- `username`: Login username (unique)
- `password_hash`: Hashed password (use bcrypt)
- `full_name`: Arabic name to display
- `role`: 'manager' or 'cashier'
- `is_active`: 1=active, 0=disabled

---

#### Table: `categories`
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields Explanation:**
- `name`: Category name in Arabic (كريب، بيتزا، مشروبات)
- `display_order`: Order to show in UI
- `is_active`: Show/hide category

---

#### Table: `items`
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    image_path TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**Fields Explanation:**
- `category_id`: Links to categories table
- `name`: Item name in Arabic
- `price`: Price in EGP
- `image_path`: Optional image file path
- `is_active`: Available/unavailable

---

#### Table: `inventory`
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    current_quantity REAL DEFAULT 0,
    unit TEXT NOT NULL,
    min_alert_quantity REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields Explanation:**
- `name`: Material name (دقيق، جبنة، زيت)
- `current_quantity`: Current stock
- `unit`: Unit of measure (كيلو، جرام، لتر، قطعة، كيس)
- `min_alert_quantity`: Alert when stock reaches this level

---

#### Table: `recipes`
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id),
    UNIQUE(item_id, inventory_id)
);
```

**Fields Explanation:**
- Links menu items to inventory
- `quantity`: How much of inventory item is used per sale
- Example: Cheese Crepe = 1 dough + 50g cheese

---

#### Table: `orders`
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    employee_id INTEGER NOT NULL,
    shift_id INTEGER,
    table_id INTEGER,
    order_type TEXT DEFAULT 'takeaway' CHECK(order_type IN ('takeaway', 'dine-in')),
    total REAL NOT NULL,
    payment_method TEXT DEFAULT 'cash',
    status TEXT DEFAULT 'completed' CHECK(status IN ('completed', 'cancelled', 'returned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (shift_id) REFERENCES shifts(id),
    FOREIGN KEY (table_id) REFERENCES tables(id)
);
```

**Fields Explanation:**
- `order_number`: Auto-generated unique number (e.g., "ORD-20240101-0001")
- `table_id`: NULL for takeaway
- `order_type`: 'takeaway' or 'dine-in'
- `status`: 'completed', 'cancelled', 'returned'

---

#### Table: `order_items`
```sql
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);
```

**Fields Explanation:**
- Links orders to items
- `price`: Price at time of sale (may differ from current price)
- `subtotal`: quantity × price

---

#### Table: `shifts`
```sql
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_name TEXT NOT NULL CHECK(shift_name IN ('صباحي', 'مسائي')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    total_sales REAL DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    cash_collected REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

**Fields Explanation:**
- `shift_name`: 'صباحي' or 'مسائي'
- `ended_at`: NULL while shift is active
- `total_sales`: Calculated when shift closes
- `is_active`: 1=open, 0=closed

---

#### Table: `returns`
```sql
CREATE TABLE returns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    return_type TEXT NOT NULL CHECK(return_type IN ('full', 'partial')),
    amount REAL NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

**Fields Explanation:**
- `return_type`: 'full' = entire order, 'partial' = some items
- `amount`: Money refunded

---

#### Table: `settings`
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Purpose:** Store app-level settings
- `tables_enabled`: '0' or '1'
- `printer_enabled`: '0' or '1'
- etc.

---

#### Table: `tables` (Optional)
```sql
CREATE TABLE tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number TEXT UNIQUE NOT NULL,
    is_occupied INTEGER DEFAULT 0,
    current_order_id INTEGER,
    FOREIGN KEY (current_order_id) REFERENCES orders(id)
);
```

---

### 3.3 Initial Data

#### Default Admin Account
```sql
INSERT INTO employees (username, password_hash, full_name, role) 
VALUES ('admin', '<bcrypt_hash>', 'المدير', 'manager');
```

#### Default Settings
```sql
INSERT INTO settings (key, value) VALUES 
('tables_enabled', '0'),
('printer_enabled', '0'),
('thank_you_message', 'شكراً لزيارتكم');
```

---

## 4. PROJECT STRUCTURE

```
restaurant_app/
│
├── main.py                         # Entry point
├── CLAUDE.md                       # This file
├── requirements.txt                # Python dependencies
├── config.encrypted                # Restaurant customization (created on setup)
│
├── assets/
│   ├── logo.png                    # Restaurant logo
│   └── icons/                      # UI icons
│       ├── pos.png
│       ├── inventory.png
│       ├── reports.png
│       └── settings.png
│
├── database/
│   ├── db_manager.py               # Database connection & queries
│   ├── schema.sql                  # Database schema
│   └── restaurant.db               # SQLite database (created on first run)
│
├── ui/
│   ├── login_window.py             # Login screen
│   ├── main_window.py              # Main navigation window
│   ├── pos_window.py               # POS/Cashier screen
│   ├── inventory_window.py         # Inventory management
│   ├── reports_window.py           # Reports & analytics
│   ├── employees_window.py         # Employee management
│   ├── menu_window.py              # Menu/items management
│   ├── settings_window.py          # Settings
│   └── components/                 # Reusable UI components
│       ├── invoice_dialog.py       # Invoice preview
│       └── shift_dialog.py         # Shift management
│
├── modules/
│   ├── auth.py                     # Authentication logic
│   ├── orders.py                   # Order processing
│   ├── inventory.py                # Inventory operations
│   ├── shifts.py                   # Shift management
│   ├── reports.py                  # Report generation
│   └── returns.py                  # Returns/refunds
│
├── utils/
│   ├── config.py                   # Config file encryption/decryption
│   ├── printer.py                  # Thermal printer integration
│   ├── pdf_generator.py            # PDF export
│   ├── excel_generator.py          # Excel export
│   └── backup.py                   # Database backup
│
└── exports/                        # Generated reports
    ├── pdf/
    └── excel/
```

---

## 5. UI/UX SPECIFICATIONS

### 5.1 General UI Rules

#### Language & Direction
- **All text in Arabic**
- **RTL (Right-to-Left) layout**
- Font: Use system Arabic font (Segoe UI, Tahoma)
- Font sizes:
  - Headers: 16-18pt Bold
  - Body: 12-14pt
  - Buttons: 14pt

#### Colors
- Will be customizable via config.encrypted
- Default theme:
  - Primary: #2C3E50 (Dark blue)
  - Secondary: #27AE60 (Green)
  - Background: #ECF0F1 (Light gray)
  - Text: #2C3E50
  - Danger: #E74C3C (Red)

#### Window Sizes
- Login: 400×500 (fixed, centered)
- Main: 1200×800 (resizable, maximized by default)
- Dialogs: Appropriate size, centered on parent

---

### 5.2 Screen-by-Screen Layout

#### 5.2.1 Login Window

```
┌─────────────────────────────────────┐
│          [LOGO]                     │
│      اسم المطعم                     │
│                                     │
│  اسم المستخدم: [_______________]   │
│                                     │
│  كلمة المرور:   [_______________]   │
│                                     │
│         [ تسجيل الدخول ]            │
│                                     │
└─────────────────────────────────────┘
```

**Behavior:**
- Show logo from config
- Press Enter to submit
- Hash password before checking DB
- On success: Open Main Window
- On fail: Show error message

---

#### 5.2.2 Main Window (Navigation)

```
┌────────────────────────────────────────────────────────┐
│  [اسم المطعم]                      [المستخدم: أحمد] ▼  │
├────────────────────────────────────────────────────────┤
│                                                        │
│   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │
│   │ نقطة │  │      │  │ تقارير│  │إعدادات│  │موظفين│  │
│   │ البيع│  │المخزون│  │      │  │      │  │      │  │
│   └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  │
│                                                        │
│   ┌──────┐  ┌──────┐  ┌──────┐                       │
│   │القائمة│  │الشفتات│  │مرتجعات│                      │
│   │      │  │      │  │      │                       │
│   └──────┘  └──────┘  └──────┘                       │
│                                                        │
│                                                        │
│  الشفت الحالي: صباحي - أحمد                           │
│  بدأ الساعة: 08:00 ص                                  │
│                                                        │
│  [ إنهاء الشفت ]                 [ تسجيل الخروج ]     │
└────────────────────────────────────────────────────────┘
```

**Behavior:**
- Large icon buttons for main functions
- Show current shift info at bottom
- Manager sees all buttons
- Cashier sees limited buttons (based on role)

---

#### 5.2.3 POS Window (Most Important Screen)

```
┌────────────────────────────────────────────────────────────────┐
│  نقطة البيع                         رقم الأوردر: ORD-20240101-0001 │
├─────────────────────────────┬──────────────────────────────────┤
│                             │                                  │
│  ┌──────────────────────┐   │   الطلب الحالي                    │
│  │  بحث...             │   │  ┌────────────────────────────┐  │
│  └──────────────────────┘   │  │ كريب جبنة    ×2    40 ج.م  │  │
│                             │  │ بيتزا مارجريتا ×1   60 ج.م  │  │
│  الأقسام                    │  │ كولا         ×1    10 ج.م  │  │
│  ┌──────┐ ┌──────┐          │  │                            │  │
│  │كريبات│ │بيتزا │          │  │                            │  │
│  └──────┘ └──────┘          │  │                            │  │
│  ┌──────┐ ┌──────┐          │  │                            │  │
│  │برجر │ │مشروبات│          │  └────────────────────────────┘  │
│  └──────┘ └──────┘          │                                  │
│                             │  [ - ]  الكمية: 1  [ + ]         │
│  الأصناف (كريبات)           │  [ حذف الصنف ]                    │
│  ┌──────┐ ┌──────┐          │                                  │
│  │كريب  │ │كريب  │          │  ─────────────────────────────   │
│  │جبنة  │ │نوتيلا│          │  الإجمالي:        110.00 ج.م    │
│  │20 ج.م│ │25 ج.م│          │                                  │
│  └──────┘ └──────┘          │  [ تيك أواي ]  [ طاولة رقم: __ ] │
│  ┌──────┐ ┌──────┐          │                                  │
│  │كريب  │ │كريب  │          │  ┌──────────┐  ┌──────────┐     │
│  │موز   │ │فراولة│          │  │ إلغاء    │  │ دفــع    │     │
│  │20 ج.م│ │20 ج.م│          │  └──────────┘  └──────────┘     │
│  └──────┘ └──────┘          │                                  │
│                             │                                  │
└─────────────────────────────┴──────────────────────────────────┘
```

**Behavior:**
- Click category → Show items for that category
- Click item → Add to current order
- Search bar → Filter items by name
- Quantity buttons → Adjust item quantity
- Delete → Remove from order
- Cancel → Clear entire order
- Pay → Process payment & print invoice
- If tables enabled → Show table option

---

#### 5.2.4 Invoice Dialog

```
┌─────────────────────────────┐
│      اسم المطعم             │
│      العنوان - التليفون     │
├─────────────────────────────┤
│  رقم الأوردر: ORD-...-0001  │
│  التاريخ: 2024/01/15        │
│  الوقت: 02:30 م             │
│  ────────────────────────   │
│  كريب جبنة    ×2    40.00   │
│  بيتزا مارجريتا ×1   60.00   │
│  كولا         ×1    10.00   │
│  ────────────────────────   │
│  الإجمالي:         110.00   │
│                             │
│  شكراً لزيارتكم             │
├─────────────────────────────┤
│  [ طباعة ]      [ إغلاق ]  │
└─────────────────────────────┘
```

---

#### 5.2.5 Inventory Window

```
┌────────────────────────────────────────────────────────────────┐
│  المخزون                                        [ إضافة مادة ] │
├────────────────────────────────────────────────────────────────┤
│  بحث: [_______________]                                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ المادة       │ الكمية الحالية │ الوحدة │ الحد الأدنى   │ │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ دقيق        │ 50.0          │ كيلو   │ 10.0         │🔴│ │
│  │ جبنة شيدر   │ 25.5          │ كيلو   │ 5.0          │✅│ │
│  │ زيت         │ 8.0           │ لتر    │ 3.0          │✅│ │
│  │ كيس ستريبس  │ 3.0           │ كيس    │ 5.0          │🔴│ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  [ تعديل ]  [ إضافة كمية ]  [ سجل التعديلات ]                 │
└────────────────────────────────────────────────────────────────┘
```

**Behavior:**
- Red indicator 🔴 when quantity ≤ min_alert_quantity
- Click row → Enable edit/add quantity buttons
- Add quantity → Dialog to add purchased stock

---

#### 5.2.6 Reports Window

```
┌────────────────────────────────────────────────────────────────┐
│  التقارير                                                      │
├────────────────────────────────────────────────────────────────┤
│  نوع التقرير: [▼ يومي     ]                                   │
│  من: [____] إلى: [____]                                       │
│  [ عرض ]                                                       │
│  ────────────────────────────────────────────────────────────  │
│  📊 ملخص المبيعات                                              │
│     إجمالي المبيعات: 2,500.00 ج.م                             │
│     عدد الأوردرات: 45                                          │
│     متوسط الأوردر: 55.56 ج.م                                  │
│  ────────────────────────────────────────────────────────────  │
│  📈 الأصناف الأكثر مبيعاً                                      │
│     1. كريب جبنة - 25 قطعة                                     │
│     2. بيتزا مارجريتا - 18 قطعة                                │
│     3. برجر لحم - 12 قطعة                                      │
│  ────────────────────────────────────────────────────────────  │
│  [ تصدير PDF ]  [ تصدير Excel ]                               │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. DETAILED PARTS IMPLEMENTATION

---

## PART 1: Project Setup & Database

### 🎯 Goal
Create project structure, install dependencies, setup database with schema and initial data.

---

### 📋 Tasks

#### 1.1 Create Project Structure
Create all folders and empty files as per structure in Section 4.

#### 1.2 Create `requirements.txt`
```txt
PyQt6==6.6.0
reportlab==4.0.7
openpyxl==3.1.2
cryptography==41.0.7
Pillow==10.1.0
bcrypt==4.1.2
```

#### 1.3 Create `database/schema.sql`
Copy the complete SQL schema from Section 3.2.

#### 1.4 Create `database/db_manager.py`

**Purpose:** Handle all database operations

**Required Functions:**

```python
class DatabaseManager:
    def __init__(self, db_path: str):
        """Initialize connection to SQLite database"""
        
    def execute_schema(self, schema_file: str):
        """Execute schema.sql to create tables"""
        
    def insert_default_data(self):
        """Insert default admin and settings"""
        
    def get_connection(self):
        """Return database connection"""
        
    def execute_query(self, query: str, params: tuple = ()):
        """Execute INSERT/UPDATE/DELETE"""
        
    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch single row"""
        
    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch multiple rows"""
        
    def close(self):
        """Close connection"""
```

**Implementation Details:**
- Use `sqlite3` module
- Create database file if doesn't exist
- Execute schema on first run
- Use parameterized queries (prevent SQL injection)
- Hash default admin password with bcrypt

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123` (hashed with bcrypt before storing)

---

#### 1.5 Create `main.py` (Initial Version)

```python
import sys
from PyQt6.QtWidgets import QApplication
from database.db_manager import DatabaseManager

def main():
    # Initialize database
    db = DatabaseManager('database/restaurant.db')
    
    # Check if database is new (first run)
    if not db.tables_exist():
        print("First run detected. Creating database...")
        db.execute_schema('database/schema.sql')
        db.insert_default_data()
        print("Database created successfully!")
    
    # Initialize Qt Application
    app = QApplication(sys.argv)
    
    # TODO: Show login window (will be done in PART 3)
    print("Application started!")
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

---

### ✅ Checklist for PART 1

Before proceeding to PART 2, verify:

- [x] All folders created as per structure
- [x] `requirements.txt` created with correct versions
- [x] `schema.sql` contains all 11 tables
- [x] `db_manager.py` has all required functions
- [x] Database file created on first run
- [x] Tables created successfully
- [x] Default admin account inserted (verify with DB browser)
- [x] Default settings inserted
- [x] Admin password is hashed (not plain text)
- [x] `main.py` runs without errors
- [x] No import errors

**Test Command:**
```bash
python main.py
```

**Expected Output:**
```
First run detected. Creating database...
Database created successfully!
Application started!
```

---

## PART 2: Configuration System

### 🎯 Goal
Create encrypted configuration file system for restaurant customization.

---

### 📋 Configuration Structure

The `config.encrypted` file will contain:

```json
{
  "restaurant": {
    "name": "مطعم الكريب الذهبي",
    "name_english": "Golden Crepe Restaurant",
    "address": "123 شارع الهرم، الجيزة",
    "phone": "0123456789",
    "tax_id": ""
  },
  "branding": {
    "logo_path": "assets/logo.png",
    "primary_color": "#2C3E50",
    "secondary_color": "#27AE60"
  },
  "invoice": {
    "thank_you_message": "شكراً لزيارتكم",
    "footer_note": ""
  },
  "features": {
    "tables_enabled": false,
    "printer_enabled": false
  },
  "shifts": {
    "available_shifts": ["صباحي", "مسائي"]
  }
}
```

---

### 📋 Tasks

#### 2.1 Create `utils/config.py`

**Required Functions:**

```python
from cryptography.fernet import Fernet
import json

class ConfigManager:
    def __init__(self, config_path: str, key_path: str):
        """Initialize with paths to config and encryption key"""
        
    def generate_key(self):
        """Generate encryption key (done once by developer)"""
        
    def encrypt_config(self, data: dict):
        """Encrypt and save config file"""
        
    def decrypt_config(self) -> dict:
        """Load and decrypt config file"""
        
    def get(self, key_path: str):
        """
        Get config value by dot notation
        Example: get('restaurant.name')
        """
        
    def update(self, key_path: str, value):
        """Update config value and re-encrypt"""
```

**Implementation Details:**
- Use `cryptography.fernet` for symmetric encryption
- Store encryption key in `.key` file (developer keeps this)
- Config file is JSON encrypted as binary
- Support nested keys with dot notation

---

#### 2.2 Create Setup Tool `setup_restaurant.py`

**Purpose:** Developer uses this to customize config for each restaurant

```python
from utils.config import ConfigManager
import json

def setup_restaurant():
    """Interactive setup for new restaurant"""
    
    print("=== Restaurant Setup ===\n")
    
    config = {
        "restaurant": {
            "name": input("اسم المطعم (عربي): "),
            "name_english": input("Restaurant Name (English): "),
            "address": input("العنوان: "),
            "phone": input("رقم التليفون: "),
            "tax_id": input("الرقم الضريبي (اختياري): ")
        },
        "branding": {
            "logo_path": input("مسار اللوجو (مثال: assets/logo.png): "),
            "primary_color": input("اللون الرئيسي (مثال: #2C3E50): ") or "#2C3E50",
            "secondary_color": input("اللون الثانوي (مثال: #27AE60): ") or "#27AE60"
        },
        "invoice": {
            "thank_you_message": input("رسالة الشكر في الفاتورة: ") or "شكراً لزيارتكم",
            "footer_note": input("ملاحظة إضافية (اختياري): ")
        },
        "features": {
            "tables_enabled": input("تفعيل الطاولات؟ (yes/no): ").lower() == 'yes',
            "printer_enabled": input("تفعيل الطابعة؟ (yes/no): ").lower() == 'yes'
        },
        "shifts": {
            "available_shifts": ["صباحي", "مسائي"]
        }
    }
    
    # Save encrypted config
    cm = ConfigManager('config.encrypted', 'config.key')
    cm.encrypt_config(config)
    
    print("\n✅ Configuration saved successfully!")
    print("📄 File: config.encrypted")

if __name__ == '__main__':
    setup_restaurant()
```

---

#### 2.3 Update `main.py`

Add config loading:

```python
from utils.config import ConfigManager

def main():
    # Load config
    try:
        config = ConfigManager('config.encrypted', 'config.key')
        restaurant_name = config.get('restaurant.name')
        print(f"Loading: {restaurant_name}")
    except FileNotFoundError:
        print("Error: config.encrypted not found!")
        print("Run setup_restaurant.py first")
        return
    
    # ... rest of code
```

---

### ✅ Checklist for PART 2

- [x] `utils/config.py` created with all functions
- [x] Encryption/decryption works correctly
- [x] `setup_restaurant.py` runs and creates `config.encrypted`
- [x] `config.key` file created (keep this secure!)
- [x] Config can be read in `main.py`
- [x] Dot notation works (e.g., `config.get('restaurant.name')`)
- [x] File is encrypted (not readable in text editor)

**Test:**
```bash
python setup_restaurant.py
python main.py
```

---

## PART 3: Authentication & Employees

### 🎯 Goal
Create login system and employee management.

---

### 📋 Tasks

#### 3.1 Create `modules/auth.py`

**Required Functions:**

```python
import bcrypt
from database.db_manager import DatabaseManager

class AuthManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        
    def verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash"""
        
    def login(self, username: str, password: str) -> dict|None:
        """
        Attempt login
        Returns: user dict if success, None if failed
        """
        
    def logout(self):
        """Clear current user"""
        
    def get_current_user(self) -> dict|None:
        """Get currently logged in user"""
        
    def is_manager(self) -> bool:
        """Check if current user is manager"""
        
    def is_cashier(self) -> bool:
        """Check if current user is cashier"""
```

**Implementation:**
```python
def login(self, username: str, password: str) -> dict|None:
    # Fetch user from database
    user = self.db.fetch_one(
        "SELECT * FROM employees WHERE username = ? AND is_active = 1",
        (username,)
    )
    
    if not user:
        return None
    
    # Verify password
    if self.verify_password(password, user['password_hash']):
        self.current_user = user
        return user
    
    return None
```

---

#### 3.2 Create `ui/login_window.py`

**Layout:** As shown in Section 5.2.1

**Required Elements:**
- Logo (from config)
- Restaurant name label (from config)
- Username input (QLineEdit)
- Password input (QLineEdit, password mode)
- Login button
- Error label (hidden by default)

**Behavior:**
```python
class LoginWindow(QWidget):
    def __init__(self, db, config, auth):
        # Initialize UI
        # Load logo from config
        # Set restaurant name
        
    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        user = self.auth.login(username, password)
        
        if user:
            # Open main window
            self.open_main_window()
        else:
            # Show error
            self.error_label.setText("اسم المستخدم أو كلمة المرور غير صحيحة")
```

**Styling:**
- RTL layout
- Arabic font
- Colors from config
- Center on screen

---

#### 3.3 Create `ui/employees_window.py`

**Layout:**

```
┌────────────────────────────────────────────────────┐
│  الموظفين                           [ إضافة موظف ] │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │ الاسم    │ اسم المستخدم │ الدور   │ الحالة │ │ │
│  ├──────────────────────────────────────────────┤ │
│  │ أحمد محمد │ ahmed       │ كاشير  │ نشط   │✏️│ │
│  │ محمد علي  │ mohamed     │ مدير   │ نشط   │✏️│ │
│  └──────────────────────────────────────────────┘ │
│  [ تعديل ]  [ تعطيل/تفعيل ]  [ تغيير كلمة المرور ] │
└────────────────────────────────────────────────────┘
```

**Features:**
- List all employees
- Add new employee (dialog)
- Edit employee
- Activate/deactivate
- Change password

**Add Employee Dialog:**
- Full name
- Username
- Password
- Role (dropdown: مدير / كاشير)

**Permissions:**
- Only managers can access this screen

---

#### 3.4 Update `main.py`

```python
from ui.login_window import LoginWindow
from modules.auth import AuthManager

def main():
    # ... database and config setup ...
    
    # Initialize auth
    auth = AuthManager(db)
    
    # Show login window
    login_window = LoginWindow(db, config, auth)
    login_window.show()
    
    sys.exit(app.exec())
```

---

### ✅ Checklist for PART 3

- [x] `modules/auth.py` created with all functions
- [x] Password hashing works with bcrypt
- [x] Login validation works correctly
- [x] Login window displays with logo and restaurant name
- [x] RTL layout works properly
- [x] Successful login opens next window
- [x] Failed login shows error message
- [x] Employees window shows list of employees
- [x] Can add new employee
- [x] Can edit existing employee
- [x] Can deactivate employee
- [x] Only managers can access employees screen
- [x] Current user info stored in auth manager

### ✅ Checklist for PART 3

- [x] `modules/auth.py` created with all functions (enhanced)
- [x] Password hashing works (salt+sha256 implementation)
- [x] Login validation works correctly
- [x] Login window displays with logo and restaurant name
- [x] RTL layout works properly
- [x] Successful login opens next window
- [x] Failed login shows error message
- [x] Employees window shows list of employees
- [x] Can add new employee (via UI and API)
- [x] Can edit existing employee (backend API `update_employee` available)
- [x] Can deactivate employee (backend API available)
- [x] Only managers can access employees screen
- [x] Current user info stored in auth manager (`current_user`)

**Test:**
- Login with default admin (admin/admin123)
- Try wrong password (should fail)
- Add new employee
- Try login with new employee

---

## PART 4: Main Window & Navigation

### 🎯 Goal
Create main navigation window with role-based menu.

---

### 📋 Tasks

#### 4.1 Create `ui/main_window.py`

**Layout:** As shown in Section 5.2.2

**Required Elements:**
- Header with restaurant name and user dropdown
- Navigation buttons (large icons + text):
  - نقطة البيع (POS)
  - المخزون (Inventory)
  - التقارير (Reports)
  - القائمة (Menu)
  - الشفتات (Shifts)
  - المرتجعات (Returns)
  - الموظفين (Employees) - Manager only
  - الإعدادات (Settings) - Manager only
- Current shift info (bottom)
- End shift button
- Logout button

**Role-Based Display:**

| Button | Cashier | Manager |
|--------|---------|---------|
| POS | ✅ | ✅ |
| Inventory | ❌ | ✅ |
| Reports | ✅ | ✅ |
| Menu | ❌ | ✅ |
| Shifts | ✅ | ✅ |
| Returns | ✅ | ✅ |
| Employees | ❌ | ✅ |
| Settings | ❌ | ✅ |

**Implementation:**

```python
class MainWindow(QMainWindow):
    def __init__(self, db, config, auth):
        self.db = db
        self.config = config
        self.auth = auth
        
        self.init_ui()
        self.load_current_shift()
        
    def init_ui(self):
        # Create navigation buttons
        # Show/hide based on role
        
    def load_current_shift(self):
        # Check if user has active shift
        # Display shift info
        
    def open_pos(self):
        # Open POS window
        
    def open_inventory(self):
        # Open inventory window
        
    # ... other navigation methods
    
    def logout(self):
        self.auth.logout()
        self.close()
        # Show login window again
```

---

#### 4.2 Create Shift Check Logic

**Requirement:** Before cashier can use POS, must have active shift.

```python
def check_shift_required(self):
    """Check if current user has active shift"""
    user_id = self.auth.get_current_user()['id']
    
    active_shift = self.db.fetch_one(
        "SELECT * FROM shifts WHERE employee_id = ? AND is_active = 1",
        (user_id,)
    )
    
    return active_shift
```

**Behavior:**
- If no active shift → Show "Start Shift" dialog
- If active shift exists → Allow POS access

---

#### 4.3 Create Start Shift Dialog

```
┌─────────────────────────────┐
│  بدء شفت جديد               │
├─────────────────────────────┤
│  الموظف: أحمد محمد          │
│                             │
│  اختر الشفت:                │
│  ⚫ صباحي                    │
│  ⚪ مسائي                    │
│                             │
│  [ بدء ]      [ إلغاء ]     │
└─────────────────────────────┘
```

**On Start:**
```sql
INSERT INTO shifts (employee_id, shift_name, started_at, is_active)
VALUES (?, ?, CURRENT_TIMESTAMP, 1)
```

---

#### 4.4 Create End Shift Dialog

```
┌──────────────────────────────────┐
│  إنهاء الشفت                     │
├──────────────────────────────────┤
│  الشفت: صباحي                    │
│  بدأ الساعة: 08:00 ص             │
│  المدة: 6 ساعات و 30 دقيقة       │
│  ──────────────────────────────  │
│  إجمالي المبيعات: 2,500.00 ج.م  │
│  عدد الأوردرات: 45               │
│  كاش محصل: 2,500.00 ج.م          │
│  ──────────────────────────────  │
│  [ طباعة التقرير ]               │
│  [ إنهاء الشفت ]                 │
└──────────────────────────────────┘
```

**On End:**
```sql
UPDATE shifts 
SET ended_at = CURRENT_TIMESTAMP,
    total_sales = ?,
    total_orders = ?,
    cash_collected = ?,
    is_active = 0
WHERE id = ?
```

---

### ✅ Checklist for PART 4

- [x] Main window displays with all buttons
- [x] Buttons show/hide based on user role
- [x] Restaurant name shown in header
- [x] User dropdown shows current user
- [x] Current shift info displayed
- [x] Start shift dialog works
- [x] Shift created in database
- [x] End shift calculates totals correctly
- [x] End shift updates database
- [x] Logout works and returns to login
- [x] Navigation buttons open respective windows (placeholder windows OK for now)

---

## PART 5: Menu Management

### 🎯 Goal
Create interface to manage categories and menu items.

---

### 📋 Tasks

#### 5.1 Create `ui/menu_window.py`

**Layout:**

```
┌────────────────────────────────────────────────────────────────┐
│  القائمة                                                        │
├──────────────────────┬─────────────────────────────────────────┤
│  الأقسام            │  الأصناف                                 │
│  ┌────────────────┐ │  القسم: كريبات               [ إضافة ]  │
│  │ كريبات      ✏️ │ │  ┌──────────────────────────────────┐   │
│  │ بيتزا       ✏️ │ │  │ اسم الصنف   │ السعر │ متاح │     │   │
│  │ برجر        ✏️ │ │  ├──────────────────────────────────┤   │
│  │ مشروبات     ✏️ │ │  │ كريب جبنة   │ 20   │ ✅   │ ✏️  │   │
│  └────────────────┘ │  │ كريب نوتيلا │ 25   │ ✅   │ ✏️  │   │
│  [ إضافة قسم ]     │  │ كريب موز    │ 20   │ ❌   │ ✏️  │   │
│                    │  └──────────────────────────────────┘   │
│                    │  [ تعديل ]  [ تفعيل/تعطيل ]  [ حذف ]   │
└────────────────────┴─────────────────────────────────────────┘
```

---

#### 5.2 Categories Management

**Add Category Dialog:**
- اسم القسم
- ترتيب العرض (number)

**Database:**
```sql
INSERT INTO categories (name, display_order) VALUES (?, ?)
```

**Edit Category:**
- Same fields
```sql
UPDATE categories SET name = ?, display_order = ? WHERE id = ?
```

---

#### 5.3 Items Management

**Add Item Dialog:**
```
┌─────────────────────────────┐
│  إضافة صنف جديد             │
├─────────────────────────────┤
│  القسم: [▼ كريبات      ]   │
│  اسم الصنف: [___________]  │
│  السعر: [___________] ج.م   │
│  صورة: [اختر صورة...]      │
│  [ ] متاح للبيع             │
│                             │
│  ─── الربط بالمخزون ───     │
│  [ إضافة مكون ]             │
│  ┌───────────────────────┐  │
│  │ دقيق   - 0.2 كيلو    │  │
│  │ جبنة   - 50 جرام     │  │
│  └───────────────────────┘  │
│                             │
│  [ حفظ ]      [ إلغاء ]    │
└─────────────────────────────┘
```

**Recipe Linking:**
- Button "إضافة مكون" opens dialog:
  - Select inventory item (dropdown)
  - Enter quantity
  - Unit displayed automatically

**Database:**
```sql
-- Insert item
INSERT INTO items (category_id, name, price, image_path, is_active)
VALUES (?, ?, ?, ?, ?)

-- Insert recipe links
INSERT INTO recipes (item_id, inventory_id, quantity)
VALUES (?, ?, ?)
```

---

#### 5.4 Image Handling

**Requirements:**
- Allow PNG/JPG
- Copy to `assets/items/` folder
- Store relative path in database
- Display thumbnail in item list

```python
def save_item_image(self, source_path: str, item_id: int) -> str:
    """Copy image to assets folder and return path"""
    import shutil
    from pathlib import Path
    
    # Create directory if not exists
    Path("assets/items").mkdir(exist_ok=True)
    
    # Generate filename
    ext = Path(source_path).suffix
    filename = f"item_{item_id}{ext}"
    dest_path = f"assets/items/{filename}"
    
    # Copy file
    shutil.copy(source_path, dest_path)
    
    return dest_path
```

---

### ✅ Checklist for PART 5

- [x] Menu window displays categories and items
- [x] Can add new category
- [ ] Can edit category
- [ ] Categories sorted by display_order
- [ ] Can add new item with all fields
- [ ] Image upload and copy works
- [ ] Images display in item list
- [ ] Can link item to inventory (recipes)
- [ ] Recipe links saved correctly
- [ ] Can edit existing item
- [ ] Can activate/deactivate item
- [x] Inactive items marked clearly
- [x] Only managers can access menu management

**Test:**
- Add category "كريبات"
- Add item "كريب جبنة" with price 20
- Upload image
- Link to inventory (if inventory items exist)
- Verify in database

---

## PART 6: POS / Cashier Screen

### 🎯 Goal
Create the point-of-sale interface for taking orders.

---

### 📋 Tasks

#### 6.1 Create `ui/pos_window.py`

**Layout:** As shown in Section 5.2.3

**UI Components:**

**Left Panel:**
- Search bar (QLineEdit)
- Category buttons (dynamic from database)
- Item buttons (dynamic based on selected category)

**Right Panel:**
- Order number (auto-generated)
- Current order items (QTableWidget)
- Quantity controls (+/-)
- Delete item button
- Order type selector (تيك أواي / طاولة)
- Total display (large, bold)
- Cancel and Pay buttons

---

#### 6.2 Order Number Generation

**Format:** `ORD-YYYYMMDD-####`

**Example:** `ORD-20240115-0001`

```python
def generate_order_number(self) -> str:
    from datetime import datetime
    
    today = datetime.now().strftime('%Y%m%d')
    prefix = f"ORD-{today}-"
    
    # Get last order number for today
    last_order = self.db.fetch_one(
        "SELECT order_number FROM orders WHERE order_number LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}%",)
    )
    
    if last_order:
        last_num = int(last_order['order_number'].split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"
```

---

#### 6.3 Add Item to Order

```python
class POSWindow(QMainWindow):
    def __init__(self):
        self.current_order = []  # List of dict: {item_id, name, price, quantity}
        
    def add_item_to_order(self, item):
        """Add item to current order or increase quantity if exists"""
        
        # Check if item already in order
        for order_item in self.current_order:
            if order_item['item_id'] == item['id']:
                order_item['quantity'] += 1
                order_item['subtotal'] = order_item['quantity'] * order_item['price']
                self.update_order_display()
                return
        
        # Add new item
        self.current_order.append({
            'item_id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': 1,
            'subtotal': item['price']
        })
        
        self.update_order_display()
    
    def update_order_display(self):
        """Refresh the order table and total"""
        # Update QTableWidget
        # Calculate and display total
        
    def calculate_total(self) -> float:
        return sum(item['subtotal'] for item in self.current_order)
```

---

#### 6.4 Process Payment

```python
def process_payment(self):
    """Save order to database and print invoice"""
    
    if not self.current_order:
        # Show error: no items
        return
    
    # Check active shift
    shift = self.get_active_shift()
    if not shift:
        # Show error: no active shift
        return
    
    # Generate order number
    order_number = self.generate_order_number()
    
    # Get order details
    employee_id = self.auth.get_current_user()['id']
    total = self.calculate_total()
    order_type = 'takeaway'  # or 'dine-in' if table selected
    table_id = None  # or selected table_id
    
    # Insert order
    cursor = self.db.execute_query(
        """INSERT INTO orders 
           (order_number, employee_id, shift_id, table_id, order_type, total, payment_method, status)
           VALUES (?, ?, ?, ?, ?, ?, 'cash', 'completed')""",
        (order_number, employee_id, shift['id'], table_id, order_type, total)
    )
    
    order_id = cursor.lastrowid
    
    # Insert order items
    for item in self.current_order:
        self.db.execute_query(
            """INSERT INTO order_items (order_id, item_id, quantity, price, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, item['item_id'], item['quantity'], item['price'], item['subtotal'])
        )
    
    # Deduct from inventory
    self.deduct_inventory(self.current_order)
    
    # Show invoice dialog
    self.show_invoice(order_id)
    
    # Clear order
    self.current_order = []
    self.update_order_display()
```

---

#### 6.5 Inventory Deduction

```python
def deduct_inventory(self, order_items):
    """Deduct inventory based on recipes"""
    
    for item in order_items:
        # Get recipe for this item
        recipes = self.db.fetch_all(
            "SELECT inventory_id, quantity FROM recipes WHERE item_id = ?",
            (item['item_id'],)
        )
        
        for recipe in recipes:
            # Calculate total quantity to deduct
            deduct_qty = recipe['quantity'] * item['quantity']
            
            # Update inventory
            self.db.execute_query(
                "UPDATE inventory SET current_quantity = current_quantity - ? WHERE id = ?",
                (deduct_qty, recipe['inventory_id'])
            )
```

---

#### 6.6 Invoice Dialog

Create `ui/components/invoice_dialog.py`

**Layout:** As shown in Section 5.2.4

**Content:**
```python
class InvoiceDialog(QDialog):
    def __init__(self, order_id, db, config):
        # Load order details
        # Display invoice
        
    def load_order(self, order_id):
        # Get order and items from database
        # Format invoice text
        
    def print_invoice(self):
        # If printer enabled: send to thermal printer
        # Else: show print preview dialog
        
    def format_invoice_text(self) -> str:
        """Format invoice as text"""
        return f"""
        {self.config.get('restaurant.name')}
        {self.config.get('restaurant.address')}
        {self.config.get('restaurant.phone')}
        {'='*32}
        رقم الأوردر: {self.order['order_number']}
        التاريخ: {self.order['date']}
        الوقت: {self.order['time']}
        {'-'*32}
        {self.format_items()}
        {'-'*32}
        الإجمالي: {self.order['total']:.2f} ج.م
        
        {self.config.get('invoice.thank_you_message')}
        """
```

---

#### 6.7 Table Support (Optional)

**If tables enabled in config:**

Show table selector in POS:
```python
if self.config.get('features.tables_enabled'):
    # Show table dropdown/grid
    # Mark table as occupied when order started
    # Free table when order completed
```

**Table Grid Layout:**
```
┌──────┐ ┌──────┐ ┌──────┐
│ 1    │ │ 2    │ │ 3    │
│ فارغ │ │ مشغول│ │ فارغ │
└──────┘ └──────┘ └──────┘
```

---

### ✅ Checklist for PART 6

- [ ] POS window displays with correct layout
- [x] Categories loaded from database
- [x] Items loaded based on selected category
- [ ] Item buttons show name and price
- [x] Clicking item adds to order
- [ ] Quantity controls work (+/-)
- [ ] Delete item removes from order
- [x] Total calculates correctly
- [x] Order number generated correctly
- [x] Payment processes and saves to database
- [x] Order items saved correctly
- [x] Inventory deducted automatically
- [ ] Invoice dialog displays order details
- [ ] Invoice formatted correctly with all fields
- [ ] Print button works (or shows message if no printer)
- [x] Search bar filters items
- [x] Order clears after payment
- [ ] Table support works if enabled

**Test:**
- Add multiple items to order
- Change quantities
- Remove item
- Complete payment
- Check database: order saved
- Check inventory: quantities deducted
- View invoice

---

## PART 7: Inventory System

### 🎯 Goal
Manage raw materials inventory with alerts.

---

### 📋 Tasks

#### 7.1 Create `ui/inventory_window.py`

**Layout:** As shown in Section 5.2.5

**Features:**
- List all inventory items
- Color indicators for low stock
- Search/filter
- Add new material
- Edit existing
- Add quantity (purchases)
- View history

---

#### 7.2 Inventory List Display

```python
class InventoryWindow(QMainWindow):
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.init_ui()
        self.load_inventory()
        
    def load_inventory(self):
        """Load all inventory items"""
        items = self.db.fetch_all(
            "SELECT * FROM inventory ORDER BY name"
        )
        
        # Display in table
        for item in items:
            # Check if low stock
            is_low = item['current_quantity'] <= item['min_alert_quantity']
            
            # Add row with color indicator
```

**Color Indicators:**
- 🔴 Red: `current_quantity <= min_alert_quantity`
- ✅ Green: `current_quantity > min_alert_quantity`

---

#### 7.3 Add Material Dialog

```
┌─────────────────────────────┐
│  إضافة مادة جديدة           │
├─────────────────────────────┤
│  اسم المادة: [___________]  │
│  الكمية الحالية: [_____]    │
│  الوحدة: [▼ كيلو       ]   │
│  حد التنبيه: [_____]        │
│                             │
│  [ حفظ ]      [ إلغاء ]    │
└─────────────────────────────┘
```

**Units Dropdown:**
- كيلو
- جرام
- لتر
- قطعة
- كيس

**Database:**
```sql
INSERT INTO inventory (name, current_quantity, unit, min_alert_quantity)
VALUES (?, ?, ?, ?)
```

---

#### 7.4 Add Quantity (Purchase)

```
┌─────────────────────────────┐
│  إضافة كمية - دقيق          │
├─────────────────────────────┤
│  الكمية الحالية: 10.0 كيلو  │
│                             │
│  الكمية المضافة: [_____]    │
│                             │
│  الكمية الجديدة: 10.0 كيلو  │
│                             │
│  [ حفظ ]      [ إلغاء ]    │
└─────────────────────────────┘
```

**Update:**
```sql
UPDATE inventory 
SET current_quantity = current_quantity + ?,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
```

---

#### 7.5 Low Stock Alerts

**Create alert widget at top of window:**

```python
def check_low_stock(self):
    """Check for low stock items"""
    low_items = self.db.fetch_all(
        "SELECT name, current_quantity, unit FROM inventory WHERE current_quantity <= min_alert_quantity"
    )
    
    if low_items:
        # Show alert banner
        alert_text = "⚠️ تنبيه: المواد التالية منخفضة:\n"
        for item in low_items:
            alert_text += f"• {item['name']}: {item['current_quantity']} {item['unit']}\n"
        
        self.alert_label.setText(alert_text)
        self.alert_label.setVisible(True)
```

---

#### 7.6 Inventory History (Optional Enhancement)

Create `inventory_logs` table:

```sql
CREATE TABLE inventory_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    change_type TEXT NOT NULL, -- 'purchase', 'sale', 'adjustment'
    quantity_change REAL NOT NULL,
    old_quantity REAL NOT NULL,
    new_quantity REAL NOT NULL,
    reference_id INTEGER, -- order_id if from sale
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id)
);
```

Log every inventory change for tracking.

---

### ✅ Checklist for PART 7

- [x] Inventory window displays all materials
- [x] Low stock items shown in red
- [ ] Alert banner shows when low stock exists
- [x] Can add new material with all fields
- [x] Unit dropdown works
- [x] Can add quantity (purchase)
- [x] Quantity updates correctly in database
- [ ] Can edit material details
- [ ] Search/filter works
- [ ] Updated timestamp shows on changes
- [x] Inventory deduction from POS works (tested in PART 6)

**Test:**
- Add material "دقيق" with 10 kg, alert at 5 kg
- Add quantity +20 kg
- Verify new quantity is 30 kg
- Make sale from POS that uses this material
- Verify quantity deducted
- Set quantity below alert level
- Verify alert shows

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

- [ ] Start shift dialog works
- [ ] Shift created in database with is_active=1
- [ ] Only one active shift per employee at a time
- [ ] End shift calculates totals correctly
- [ ] End shift updates database (ended_at, totals, is_active=0)
- [ ] Shifts window shows all completed shifts
- [ ] Date filter works
- [ ] Shift details dialog displays all information
- [ ] Shift duration calculated correctly
- [ ] Print shift report works
- [ ] Can't start shift if one already active
- [ ] Can't use POS without active shift

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

- [ ] Returns window displays search interface
- [ ] Can search order by order number
- [ ] Order details display correctly
- [ ] Can select full return
- [ ] Can select partial return (select items)
- [ ] Refund amount calculates correctly
- [ ] Return processes and saves to database
- [ ] Order status updated to 'returned' (if full)
- [ ] Inventory quantities added back
- [ ] Returns history shows all returns
- [ ] Date filter works
- [ ] Can add optional reason
- [ ] Success message displays
- [ ] Cannot return already returned order

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

- [ ] Reports window displays with date range selector
- [ ] Report types dropdown works
- [ ] Sales report generates correctly
- [ ] Totals calculate correctly
- [ ] Top selling items display
- [ ] Category sales breakdown works
- [ ] Inventory report shows current stock
- [ ] Low stock items highlighted
- [ ] PDF export works
- [ ] PDF has correct Arabic text
- [ ] Excel export works
- [ ] Excel RTL layout works
- [ ] Files saved to exports folder
- [ ] Success message shows file path
- [ ] Cashier can view reports
- [ ] Manager can view all reports

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

- [ ] Settings window displays all tabs
- [ ] Restaurant info shown (read-only)
- [ ] Tables enabled checkbox works
- [ ] Printer enabled checkbox works
- [x] Thank you message editable
- [x] Save button updates database
- [ ] Success message displays
- [ ] Create backup works
- [ ] Backup file created in backups folder
- [ ] List of backups displays
- [ ] Restore backup works
- [ ] Warning shown before restore
- [ ] Delete backup works
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

- [ ] Printer utility created
- [ ] Can get list of available printers
- [ ] Invoice image generation works
- [ ] Arabic text renders correctly in image
- [ ] Print to thermal printer works
- [ ] Invoice formatted correctly (80mm width)
- [ ] Print button in invoice dialog works
- [ ] Settings has printer selection
- [ ] Test print works
- [ ] Graceful fallback if no printer
- [ ] Error handling for print failures

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

