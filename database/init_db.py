from .db import Database
import os

def initialize_database():
    """Create all tables if they don't exist"""
    db = Database()
    
    # 1. restaurants
    db.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            logo_path TEXT,
            currency TEXT DEFAULT 'ج.م',
            footer_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. menu_categories
    db.execute("""
        CREATE TABLE IF NOT EXISTS menu_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            restaurant_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)
    
    # 3. menu_items
    db.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            code TEXT UNIQUE,
            image_path TEXT,
            is_available BOOLEAN DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES menu_categories(id)
        )
    """)
    
    # 4. inventory_items
    db.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL, -- 'kg', 'g', 'l', 'ml', 'piece', 'bag'
            current_quantity REAL DEFAULT 0,
            min_quantity REAL,
            restaurant_id INTEGER,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)
    
    # 5. recipes
    db.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            inventory_item_id INTEGER NOT NULL,
            quantity REAL NOT NULL, -- quantity consumed per item sold
            FOREIGN KEY (item_id) REFERENCES menu_items(id),
            FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id)
        )
    """)
    
    # 6. employees
    db.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- 'cashier', 'manager', 'owner'
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 7. shifts
    db.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_type TEXT NOT NULL, -- 'morning', 'evening', 'night'
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            opening_balance REAL DEFAULT 0,
            closing_balance REAL,
            total_sales REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)
    
    # 8. orders
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number INTEGER NOT NULL,
            shift_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_returned BOOLEAN DEFAULT 0,
            FOREIGN KEY (shift_id) REFERENCES shifts(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)
    
    # 9. order_items
    db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_time REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        )
    """)
    
    # 10. inventory_transactions
    db.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_item_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL, -- 'purchase', 'consumption'
            quantity REAL NOT NULL,
            reference_id INTEGER, -- order_id or purchase_id
            transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id)
        )
    """)
    
    # 11. system_config
    db.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT NOT NULL UNIQUE,
            config_value TEXT,
            restaurant_id INTEGER,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)
    
    # Insert default restaurant if none exists
    restaurants = db.execute("SELECT * FROM restaurants")
    if not restaurants:
        db.execute("""
            INSERT INTO restaurants (name, currency, footer_message) 
            VALUES ('مطعمك', 'ج.م', 'شكراً لزيارتكم')
        """)

if __name__ == "__main__":
    initialize_database()
