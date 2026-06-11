import sqlite3
import bcrypt
from datetime import datetime
import os

def seed_database():
    if not os.path.exists('restaurant.db'):
        print("Database not found. Please run the app once to initialize the database.")
        return
        
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    try:
        # 1. Clear existing data (optional, but good for a fresh seed)
        # Note: We won't clear employees to preserve admin
        print("Seeding dummy data...")
        
        # 2. Add Dummy Employees (Cashiers)
        cashier1_pass = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT OR IGNORE INTO employees (username, password_hash, role) VALUES (?, ?, ?)",
                       ('cashier1', cashier1_pass.decode('utf-8'), 'cashier'))
                       
        cashier2_pass = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT OR IGNORE INTO employees (username, password_hash, role) VALUES (?, ?, ?)",
                       ('cashier2', cashier2_pass.decode('utf-8'), 'cashier'))
        
        # 3. Add Inventory Items
        inventory = [
            ('دجاج كامل', 'قطعة', 50, 10),
            ('لحم مفروم', 'كيلو', 30, 5),
            ('أرز بسمتي', 'كيلو', 100, 20),
            ('طماطم', 'كيلو', 50, 10),
            ('بصل', 'كيلو', 40, 10),
            ('خبز لبناني', 'كيس', 200, 50),
            ('بطاطس', 'كيلو', 60, 15),
            ('زيت قلي', 'لتر', 20, 5),
            ('كوكاكولا', 'علبة', 100, 20)
        ]
        
        for name, unit, qty, min_qty in inventory:
            cursor.execute("""
                INSERT INTO inventory_items (name, unit, current_quantity, min_quantity)
                SELECT ?, ?, ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM inventory_items WHERE name = ?)
            """, (name, unit, qty, min_qty, name))
            
        # 4. Add Categories
        categories = ['وجبات دجاج', 'وجبات لحوم', 'مشروبات', 'طلبات جانبية']
        for cat in categories:
            cursor.execute("""
                INSERT INTO menu_categories (name)
                SELECT ? WHERE NOT EXISTS (SELECT 1 FROM menu_categories WHERE name = ?)
            """, (cat, cat))
            
        # Get category IDs
        cursor.execute("SELECT id, name FROM menu_categories")
        cat_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # 5. Add Menu Items
        menu_items = [
            ('نصف دجاجة مشوية', cat_map['وجبات دجاج'], 120.0),
            ('كفتة مشوية', cat_map['وجبات لحوم'], 150.0),
            ('وجبة ميكس جريل', cat_map['وجبات لحوم'], 200.0),
            ('بطاطس مقلية', cat_map['طلبات جانبية'], 30.0),
            ('كوكاكولا', cat_map['مشروبات'], 15.0)
        ]
        
        for name, cat_id, price in menu_items:
            cursor.execute("""
                INSERT INTO menu_items (category_id, name, price)
                SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = ?)
            """, (cat_id, name, price, name))
            
        # Get menu item IDs and inventory IDs
        cursor.execute("SELECT id, name FROM menu_items")
        item_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, name FROM inventory_items")
        inv_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # 6. Add Recipes (Mapping menu items to inventory)
        recipes = [
            (item_map['نصف دجاجة مشوية'], inv_map['دجاج كامل'], 0.5),
            (item_map['نصف دجاجة مشوية'], inv_map['أرز بسمتي'], 0.25),
            (item_map['نصف دجاجة مشوية'], inv_map['خبز لبناني'], 1),
            
            (item_map['كفتة مشوية'], inv_map['لحم مفروم'], 0.25),
            (item_map['كفتة مشوية'], inv_map['بصل'], 0.1),
            (item_map['كفتة مشوية'], inv_map['خبز لبناني'], 2),
            
            (item_map['بطاطس مقلية'], inv_map['بطاطس'], 0.3),
            (item_map['بطاطس مقلية'], inv_map['زيت قلي'], 0.05),
            
            (item_map['كوكاكولا'], inv_map['كوكاكولا'], 1)
        ]
        
        for m_id, i_id, qty in recipes:
            cursor.execute("""
                INSERT INTO recipes (item_id, inventory_item_id, quantity)
                SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM recipes WHERE item_id = ? AND inventory_item_id = ?)
            """, (m_id, i_id, qty, m_id, i_id))
            
        conn.commit()
        print("Database successfully seeded with dummy data!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
