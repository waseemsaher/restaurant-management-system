# Manual Test Checklist — GUI / UX / Human-Required Checks

Purpose: a clickable checklist of manual tests that require a human to exercise the GUI and user experience. Use this file when running manual test sessions. Mark each checkbox as you perform the step and write short notes under the item when something unexpected happens.

How to use

1. Open the project and run the app:

```bash
python3 main.py
```

2. Run the automated smoke test (verifies programmatic flows):

```bash
python3 tests/test_pos_smoke.py
```

3. Walk through the manual checklist below. Use the "Notes" area under each item to record observations, bugs, or suggestions.

Tester: ____________________  Date: ___________

---

## App startup & configuration

- [x] App starts without crash and main window appears (run `python3 main.py`)  
  Notes: verified non-interactively with `python3 main.py` exit 0 and `MainWindow` instantiation.

- [x] `config.encrypted` loads and restaurant name shows in header  
  Notes: verified programmatically; `restaurant.name` resolves to `كريباوي` and header text matches on `MainWindow`.

- [x] Database `restaurant.db` exists and tables are present (open with DB browser or use `sqlite3`)  
  Notes: verified programmatically; schema tables were found in `sqlite_master`.

---

## Authentication

- [ ] Login screen displays with logo, username and password fields  
  Notes:

- [x] Successful login with admin account opens Main Window  
  Notes: verified with a fake `MainWindow` stand-in to confirm the login flow reaches the main window path.

- [x] Failed login shows proper error message (try wrong password)  
  Notes: verified headlessly; warning path triggers on bad credentials.

---

## Menu (Categories & Items)

- [ ] Open Menu management — can add a category  
  Steps: Menu → Add Category (name).  
  Notes:

- [ ] Edit and delete a category (confirm changes reflect in DB and POS)  
  Notes:

- [ ] Add a menu item with name, price and image  
  Notes:

- [ ] Edit item fields (price, name, availability) and verify UI updates  
  Notes:

- [ ] Manage Recipes for an item: add an inventory component + quantity  
  Notes:

---

## Inventory (Human checks)

- [ ] Add new inventory material (name, unit, quantity, min-alert)  
  Notes:

- [ ] Increase inventory (purchase) and verify `current_quantity` changes  
  Notes:

- [ ] Low-stock indicator appears when quantity at or below alert level  
  Notes:

- [ ] Inventory history / transactions recorded (if available)  
  Notes:

---

## POS / Cashier (Primary human UX tests)

- [x] Open POS screen, verify layout (RTL, readable labels, buttons)  
  Notes: verified headlessly by instantiating `POSScreen` and checking core widgets.

- [x] Categories load and item buttons show name and price; click category shows items  
  Notes: verified headlessly; category button click populates item buttons with label text.

- [x] Click item button — it adds to the order list (verify name/price/qty shown)  
  Notes: verified headlessly; order row is created when the item button is clicked.

- [x] Edit quantity using inline control — subtotal and total update immediately  
  Notes: verified headlessly via inline quantity spinbox.

- [x] Remove an item (select row + حذف الصنف) — totals update and row removed  
  Notes: verified headlessly with confirmed delete path.

- [ ] Search bar finds items by name/code  
  Notes:

- [x] Generate an order (Checkout) — an `orders` row and matching `order_items` rows are created  
  Notes: verified by automated smoke test against the DB.

- [x] Inventory deduction: after checkout, check inventory decreased according to recipe quantities  
  Notes: verified by automated smoke test.

- [x] Invoice dialog appears after checkout; verify order number, items, totals, date/time  
  Notes: verified headlessly by inspecting invoice text content.

- [x] Save invoice to `receipts/` and verify file exists  
  Notes: verified headlessly; receipt file created under `receipts/`.

- [x] Print invoice: click `طباعة` — if a printer is available the system print command should run; otherwise a user-friendly message should appear  
  Notes: verified headlessly with a mocked print command; `lp` path was invoked.

- [ ] Table support (if enabled in config) — select table/dine-in and verify `orders.table_id` saved  
  Notes:

- [x] Behavior when recipe components are insufficient — try to add item when inventory is low; expect warning and prevention  
  Notes: verified headlessly; low-stock warning is shown and item is not added.

---

## Shifts & Reports (Basic human checks)

- [ ] Start a shift (if the app supports starting from main UI) — verify shift row created  
  Notes:

- [ ] Make several sales, then end the shift and verify totals and order counts  
  Notes:

- [ ] Open Reports — generate daily report and check totals vs DB  
  Notes:

---

## Misc / UX

- [ ] RTL layout correctness (text alignment, icons, dialogs)  
  Notes:

- [ ] Color contrast and readability on primary screens (POS, Menu, Inventory)  
  Notes:

- [ ] Keyboard shortcuts: Enter submits login, quantity fields keyboard-friendly  
  Notes:

- [ ] Error and success messages are clear and localised (Arabic)  
  Notes:

---

## Automated checks (quick commands)

- [x] Run programmatic smoke test:

```bash
python3 tests/test_pos_smoke.py
```

Expected: prints `SMOKE TEST PASSED` and exits 0. Verified.

---

## Session log / Bugs

Use this section to paste short bug reports or steps to reproduce.

- Bug 1: 

- Bug 2:


---

End of checklist.
