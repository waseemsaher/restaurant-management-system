import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path
import os

class ConfigManager:
    def __init__(self, config_path: str = "config.encrypted", key_path: str = "config.key"):
        self.config_path = Path(config_path)
        self.key_path = Path(key_path)
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
        self.config = {}
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create a new one"""
        if self.key_path.exists():
            with open(self.key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
            return key
    
    def load_config(self) -> dict:
        """Load and decrypt configuration"""
        if not self.config_path.exists():
            default_config = self._get_default_config()
            self.save_config(default_config)
            self.config = default_config
            return default_config
        
        try:
            with open(self.config_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted = self.cipher.decrypt(encrypted_data)
                loaded_config = json.loads(decrypted)
                self.config = self._merge_with_defaults(loaded_config)
                return self.config
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._get_default_config()
            return self.config
    
    def save_config(self, config: dict):
        """Encrypt and save configuration"""
        config = self._normalize_config(config)
        json_data = json.dumps(config, ensure_ascii=False, indent=2).encode('utf-8')
        encrypted = self.cipher.encrypt(json_data)
        with open(self.config_path, 'wb') as f:
            f.write(encrypted)
        # keep in-memory copy in sync
        self.config = config

    # Convenience / spec-compatible API
    def generate_key(self) -> bytes:
        """Generate a new encryption key and save it to the key file (overwrites)."""
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as f:
            f.write(key)
        self.key = key
        self.cipher = Fernet(self.key)
        return key

    def encrypt_config(self, data: dict):
        """Alias for saving/encrypting config"""
        self.save_config(data)

    def decrypt_config(self) -> dict:
        """Alias for loading/decrypting config into memory and returning it"""
        return self.load_config()

    def get(self, key_path: str, default=None):
        """Get nested configuration using dot notation, e.g. 'restaurant.name'."""
        if not self.config:
            try:
                self.load_config()
            except Exception:
                return default

        parts = key_path.split('.') if key_path else []
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def update(self, key_path: str, value):
        """Update a nested configuration value via dot notation and re-encrypt the file."""
        if not self.config:
            self.load_config()

        parts = key_path.split('.') if key_path else []
        node = self.config
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]

        if parts:
            node[parts[-1]] = value
        else:
            # replace entire config
            self.config = value

        # persist change
        self.save_config(self.config)
    
    def _get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            "restaurant": {
                "name": "مطعمك",
                "address": "العنوان",
                "phone": "01234567890",
                "logo_path": "assets/logo.png",
                "currency": "ج.م",
                "footer_message": "شكراً لزيارتكم",
                "theme_color": "#2c3e50",
                "font_size": 12
            },
            "printer": {
                "enabled": False,
                "printer_name": "",
                "paper_width": 80
            },
            "tables": {
                "enabled": False,
                "table_count": 10
            },
            "shifts": {
                "morning_start": "08:00",
                "morning_end": "16:00",
                "evening_start": "16:00",
                "evening_end": "24:00"
            }
        }

    def _merge_with_defaults(self, config: dict) -> dict:
        """Merge a loaded config with defaults and normalize legacy keys."""
        defaults = self._get_default_config()
        normalized = self._merge_dicts(defaults, config if isinstance(config, dict) else {})
        return self._normalize_config(normalized)

    def _merge_dicts(self, base: dict, override: dict) -> dict:
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_dicts(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _normalize_config(self, config: dict) -> dict:
        """Fill legacy gaps so old config files continue to work."""
        normalized = self._merge_dicts(self._get_default_config(), config if isinstance(config, dict) else {})

        restaurant = normalized.setdefault("restaurant", {})
        invoice = normalized.setdefault("invoice", {})

        if not restaurant.get("footer_message") and invoice.get("thank_you_message"):
            restaurant["footer_message"] = invoice["thank_you_message"]
        if not invoice.get("thank_you_message") and restaurant.get("footer_message"):
            invoice["thank_you_message"] = restaurant["footer_message"]

        return normalized
