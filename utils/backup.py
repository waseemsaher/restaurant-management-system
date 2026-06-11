import shutil
import os
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
        
        shutil.copy(self.db_path, backup_path)
        return str(backup_path)
    
    def get_backups(self):
        """List all available backups"""
        backups = []
        for file in self.backup_dir.glob("*.db"):
            size = file.stat().st_size / 1024 # KB
            date = datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            backups.append({
                'name': file.name,
                'path': str(file),
                'size': f"{size:.2f} KB",
                'date': date
            })
        # sort by date desc
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
        
    def restore_backup(self, backup_path: str):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError("Backup file not found")
        # In a real app we might want to close DB connections first,
        # but here we'll just overwrite.
        shutil.copy(backup_path, self.db_path)
        
    def delete_backup(self, backup_path: str):
        """Delete a backup file"""
        if os.path.exists(backup_path):
            os.remove(backup_path)
