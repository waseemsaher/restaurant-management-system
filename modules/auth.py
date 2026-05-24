import typing
from typing import Optional
from database.db import Database

try:
    import bcrypt
    _HAS_BCRYPT = True
except Exception:
    bcrypt = None
    _HAS_BCRYPT = False


class AuthManager:
    def __init__(self):
        self.db = Database()
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt when available, fallback to sha256 salt."""
        if _HAS_BCRYPT:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            return hashed.decode('utf-8')
        # fallback (not recommended for production)
        import hashlib, secrets
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256(password.encode() + salt.encode())
        return salt + hash_obj.hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against stored hash."""
        if _HAS_BCRYPT:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except Exception:
                return False
        # fallback verification for sha256 variant
        import hashlib
        salt = hashed[:32]
        hash_obj = hashlib.sha256(password.encode() + salt.encode())
        return hash_obj.hexdigest() == hashed[32:]
    
    def create_employee(self, username: str, password: str, role: str, full_name: str = None) -> int:
        """Create new employee account. Returns last insert id."""
        hashed = self.hash_password(password)
        if full_name is None:
            full_name = username
        # adapt to current employees table schema (some DBs lack full_name)
        cols = [c['name'] for c in self.db.execute("PRAGMA table_info(employees)")]
        if 'full_name' in cols:
            query = "INSERT INTO employees (username, password_hash, full_name, role, is_active) VALUES (?, ?, ?, ?, 1)"
            params = (username, hashed, full_name, role)
        else:
            query = "INSERT INTO employees (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)"
            params = (username, hashed, role)
        self.db.execute_non_query(query, params)
        return self.db.get_last_insert_id()

    def login(self, username: str, password: str) -> Optional[dict]:
        """Authenticate and set current_user on success"""
        user = self.authenticate(username, password)
        if user:
            self.current_user = user
            return user
        return None

    def logout(self):
        """Clear session"""
        self.current_user = None

    def is_manager(self) -> bool:
        return bool(self.current_user and self.current_user.get('role') in ('manager', 'owner'))

    def is_cashier(self) -> bool:
        return bool(self.current_user and self.current_user.get('role') == 'cashier')

    def list_employees(self) -> list:
        """Return all employees as list of dicts"""
        return self.db.execute("SELECT * FROM employees ORDER BY username")

    def update_employee(self, employee_id: int, **kwargs) -> int:
        """Update fields for an employee. Returns affected rows."""
        allowed = ['username', 'password_hash', 'role', 'is_active']
        fields = []
        params = []
        for k, v in kwargs.items():
            if k not in allowed:
                continue
            fields.append(f"{k} = ?")
            params.append(v)
        if not fields:
            return 0
        params.append(employee_id)
        q = f"UPDATE employees SET {', '.join(fields)} WHERE id = ?"
        return self.db.execute_non_query(q, tuple(params))

    def change_password(self, employee_id: int, new_password: str) -> int:
        hashed = self.hash_password(new_password)
        return self.update_employee(employee_id, password_hash=hashed)
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user and return user dict on success."""
        users = self.db.execute(
            "SELECT * FROM employees WHERE username = ? AND is_active = 1",
            (username,)
        )
        if not users:
            return None
        user = users[0]
        stored_hash = user.get('password_hash')
        if not stored_hash:
            return None
        if self.verify_password(password, stored_hash):
            return user
        return None
    
    def get_employee_by_id(self, employee_id: int) -> Optional[dict]:
        """Get employee by ID"""
        employees = self.db.execute(
            "SELECT * FROM employees WHERE id = ?",
            (employee_id,)
        )
        return employees[0] if employees else None
