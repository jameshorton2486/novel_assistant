"""
Google Drive Sync Service
=========================

One-click backup using folder-based sync.
Recommended: Google Drive for Desktop with synced folder.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class GoogleDriveSync:
    """Handles backup to Google Drive via folder sync."""
    
    DRIVE_FOLDER_PATHS = {
        "windows": [
            Path.home() / "Google Drive",
            Path.home() / "My Drive",
            Path("G:/My Drive"),
        ],
        "darwin": [Path.home() / "Google Drive"],
        "linux": [Path.home() / "Google Drive"],
    }
    
    def __init__(self, base_dir: Path, backup_name: str = "Novel_Assistant_Backup"):
        self.base_dir = Path(base_dir)
        self.backup_name = backup_name
        self.config_path = self.base_dir / "drive_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {"drive_path": None, "last_sync": None}
    
    def _save_config(self):
        self.config_path.write_text(json.dumps(self.config, indent=2))
    
    def find_drive_folder(self) -> Optional[Path]:
        import platform
        system = platform.system().lower()
        for path in self.DRIVE_FOLDER_PATHS.get(system, []):
            if path.exists():
                return path
        return None
    
    def set_drive_folder(self, path: str) -> bool:
        drive_path = Path(path)
        if drive_path.exists():
            self.config["drive_path"] = str(drive_path)
            self._save_config()
            return True
        return False
    
    def get_backup_folder(self) -> Optional[Path]:
        if self.config.get("drive_path"):
            drive_path = Path(self.config["drive_path"])
        else:
            drive_path = self.find_drive_folder()
            if drive_path:
                self.config["drive_path"] = str(drive_path)
                self._save_config()
        
        if not drive_path or not drive_path.exists():
            return None
        
        backup_folder = drive_path / self.backup_name
        backup_folder.mkdir(exist_ok=True)
        return backup_folder
    
    def sync_folder(self, source: Path, dest_name: str) -> Dict:
        backup_folder = self.get_backup_folder()
        if not backup_folder:
            return {"success": False, "error": "Drive folder not found"}
        
        dest_folder = backup_folder / dest_name
        dest_folder.mkdir(exist_ok=True)
        
        stats = {"copied": 0, "updated": 0, "skipped": 0}
        
        for source_file in source.rglob("*"):
            if source_file.is_file():
                rel_path = source_file.relative_to(source)
                dest_file = dest_folder / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    if dest_file.exists():
                        if source_file.stat().st_mtime > dest_file.stat().st_mtime:
                            shutil.copy2(source_file, dest_file)
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        shutil.copy2(source_file, dest_file)
                        stats["copied"] += 1
                except Exception:
                    pass
        
        return {"success": True, **stats}
    
    def full_backup(self) -> Dict:
        backup_folder = self.get_backup_folder()
        if not backup_folder:
            return {"success": False, "error": "Drive folder not found"}
        
        results = {"timestamp": datetime.now().isoformat(), "folders": {}}
        
        folders = [
            ("chapters", self.base_dir / "chapters"),
            ("reference", self.base_dir / "reference"),
            ("research", self.base_dir / "research"),
            ("exports", self.base_dir / "exports"),
        ]
        
        for name, source in folders:
            if source.exists():
                results["folders"][name] = self.sync_folder(source, name)
        
        self.config["last_sync"] = results["timestamp"]
        self._save_config()
        
        return {"success": True, **results}


def backup_to_drive(base_dir: str = ".") -> Dict:
    """One-click backup."""
    sync = GoogleDriveSync(Path(base_dir))
    return sync.full_backup()
