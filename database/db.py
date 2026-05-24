import sqlite3
from typing import Optional, List, Tuple, Any
import os
import contextlib

class Database:
    def __init__(self, db_path: str = "restaurant.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {e}")
    
    def execute(self, query: str, params: tuple = ()) -> List[dict]:
        """Execute query and return results as list of dicts"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        if cursor.description is None:
            self.connection.commit()
            return []
        columns = [col[0] for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results
    
    def execute_non_query(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return rowcount"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount
    
    def get_last_insert_id(self) -> int:
        """Get last inserted row ID"""
        return self.connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    @contextlib.contextmanager
    def transaction(self):
        """Context manager for transactions"""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
