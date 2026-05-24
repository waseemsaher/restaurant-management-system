from __future__ import annotations

import bcrypt
import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def execute_schema(self, schema_file: str):
        schema_path = Path(schema_file)
        with schema_path.open('r', encoding='utf-8') as schema_handle:
            schema_sql = schema_handle.read()

        self.connection.executescript(schema_sql)
        self.connection.commit()

    def insert_default_data(self):
        default_admin = self.fetch_one("SELECT id FROM employees WHERE username = ?", ('admin',))
        if not default_admin:
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.execute_query(
                "INSERT INTO employees (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                ('admin', password_hash, 'المدير', 'manager'),
            )

        default_settings = {
            'tables_enabled': '0',
            'printer_enabled': '0',
            'thank_you_message': 'شكراً لزيارتكم',
        }
        for key, value in default_settings.items():
            existing_setting = self.fetch_one("SELECT key FROM settings WHERE key = ?", (key,))
            if not existing_setting:
                self.execute_query("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))

    def get_connection(self):
        return self.connection

    def execute_query(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def tables_exist(self) -> bool:
        row = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'employees'"
        )
        return row is not None

    def close(self):
        if self.connection:
            self.connection.close()
