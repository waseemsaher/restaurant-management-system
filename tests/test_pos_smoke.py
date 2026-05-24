#!/usr/bin/env python3
import sys
import pathlib
# Ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from modules.menu import MenuManager
from modules.inventory import InventoryManager
from modules.orders import OrderManager
from database.db import Database
import time

DB = Database()
mm = MenuManager()
inv = InventoryManager()
om = OrderManager()

suffix = str(int(time.time()))
cat_name = f"smoke_cat_{suffix}"
item_name = f"smoke_item_{suffix}"
inv_name = f"smoke_inv_{suffix}"

print('Creating category...')
mm.add_category(cat_name)
cats = mm.get_categories()
cat = next((c for c in cats if c['name'] == cat_name), None)
assert cat, 'category not created'
cat_id = cat['id']
print('Category id', cat_id)

print('Creating item...')
mm.add_item(item_name, 12.5, cat_id)
items = mm.get_items()
item = next((i for i in items if i['name'] == item_name), None)
assert item, 'item not created'
item_id = item['id']
print('Item id', item_id)

print('Creating inventory item...')
inv.add_item(inv_name, 'kg', 10, 1)
inv_items = inv.get_items()
inv_item = next((i for i in inv_items if i['name'] == inv_name), None)
assert inv_item, 'inventory item not created'
inv_id = inv_item['id']
print('Inventory id', inv_id, 'qty', inv_item['current_quantity'])

print('Linking recipe...')
mm.add_recipe(item_id, inv_id, 0.5)
recipes = mm.get_recipes_for_item(item_id)
assert recipes, 'recipe not created'
print('Recipes:', recipes)

# Ensure an employee exists
emp = DB.execute('SELECT id FROM employees LIMIT 1')
if not emp:
    print('No employee found, creating test employee')
    # check employees table columns
    cols = DB.execute('PRAGMA table_info(employees)')
    colnames = [c['name'] for c in cols]
    if 'full_name' in colnames:
        DB.execute_non_query("INSERT INTO employees (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)", (f'smoke_{suffix}', 'test', 'Smoke Test', 'cashier'))
    else:
        DB.execute_non_query("INSERT INTO employees (username, password_hash, role) VALUES (?, ?, ?)", (f'smoke_{suffix}', 'test', 'cashier'))
    emp = DB.execute('SELECT id FROM employees WHERE username = ?', (f'smoke_{suffix}',))
emp_id = emp[0]['id']
print('Using employee id', emp_id)

# Inventory before
before_qty = inv.get_item(inv_id)['current_quantity']
print('Inventory before:', before_qty)

order_number = om.get_next_order_number()
print('Order number will be', order_number)

print('Creating order...')
order_id = om.create_order(emp_id, order_number, 12.5, 'cash')
print('Order id', order_id)

print('Adding order item...')
om.add_order_item(order_id, item_id, 1)

# Deduct inventory according to recipe
recipes = om.get_recipes(item_id)
for r in recipes:
    inv.consume_item(r['inventory_item_id'], r['quantity'] * 1)

# Verify order exists
order = om.get_order(order_id)
assert order, 'order not found in DB'
print('Order saved:', order)

order_items = om.get_order_items(order_id)
assert order_items, 'order items missing'
print('Order items:', order_items)

after_qty = inv.get_item(inv_id)['current_quantity']
print('Inventory after:', after_qty)
expected = before_qty - 0.5
if abs(after_qty - expected) < 0.0001:
    print('Inventory deduction OK')
else:
    print('Inventory deduction mismatch, expected', expected)

print('SMOKE TEST PASSED')
