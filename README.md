# Restaurant Management System

Desktop restaurant management application built with Python, PyQt6, and SQLite.

## Features

- User authentication and role-based access
- Point of Sale (POS) workflow
- Menu and category management
- Inventory and recipe tracking
- Shift management
- Reports and receipt generation
- Encrypted restaurant configuration
- Arabic-ready UI (RTL layout)

## Tech Stack

- Python 3.11+
- PyQt6
- SQLite
- reportlab / openpyxl
- cryptography

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Initialize restaurant configuration:

```bash
python setup_restaurant.py
```

Start the application:

```bash
python main.py
```

On first run, if no users exist, a default admin account is created:

- Username: `admin`
- Password: `admin`

## Test

Run the smoke test:

```bash
python tests/test_pos_smoke.py
```

## Project Structure

```text
database/   # DB initialization and access layer
modules/    # Business logic (auth, menu, orders, inventory, shifts)
ui/         # PyQt6 screens and components
utils/      # Config and style helpers
tests/      # Smoke test script
main.py     # Application entry point
```

