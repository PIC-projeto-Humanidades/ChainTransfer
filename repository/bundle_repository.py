import json
from typing import Optional, List
from pathlib import Path
from database.SQLExecutor import SQLExecutor  

from pathlib import Path

# Caminho absoluto para o banco de dados
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "dtn.db"

class BundleRepository:
    def __init__(self):
        self.db = SQLExecutor(str(DB_PATH))

    # ------------------------ INSERT ------------------------
    def insert_bundle_send(
        self, 
        hash_str: str, 
        bundle: List[str], 
        status: bool = False, 
        hash_secondary: Optional[str] = None
    ):
        if hash_secondary:
            sql = """
            INSERT OR IGNORE INTO bundle_send (hash, hash_secondary, bundle, status)
            VALUES (?, ?, ?, ?)
            """
            self.db.execute(sql, (hash_str, hash_secondary, json.dumps(bundle), int(status)))
        else:
            sql = """
            INSERT OR IGNORE INTO bundle_send (hash, bundle, status)
            VALUES (?, ?, ?)
            """
            self.db.execute(sql, (hash_str, json.dumps(bundle), int(status)))

    def insert_bundle_receiver(self, hash_str: str, bundle: List[str], status: bool = False):
        sql = """
        INSERT OR IGNORE INTO bundle_receiver (hash, bundle, status)
        VALUES (?, ?, ?)
        """
        self.db.execute(sql, (hash_str, json.dumps(bundle), int(status)))

    # ------------------------ FIND ONE ------------------------
    def find_one_send(self, hash_str: str) -> Optional[dict]:
        sql = "SELECT * FROM bundle_send WHERE hash = ?"
        row = self.db.fetch_one(sql, (hash_str,))
        if row:
            row["bundle"] = json.loads(row["bundle"])  # transforma em list[str]
        return row
    def find_send_by_hash_and_secondary(self, hash_str: str, hash_secondary: str) -> Optional[dict]:
        sql = """
        SELECT * FROM bundle_send
        WHERE hash = ? AND hash_secondary = ?
        """
        row = self.db.fetch_one(sql, (hash_str, hash_secondary))
        if row:
            row["bundle"] = json.loads(row["bundle"])
        return row
        
    def find_one_receiver(self, hash_str: str) -> Optional[dict]:
        sql = "SELECT * FROM bundle_receiver WHERE hash = ?"
        row = self.db.fetch_one(sql, (hash_str,))
        if row:
            row["bundle"] = json.loads(row["bundle"])
        return row

    # ------------------------ FIND ALL ------------------------
    def find_all_send(self) -> List[dict]:
        rows = self.db.query("SELECT * FROM bundle_send")
        for row in rows:
            row["bundle"] = json.loads(row["bundle"])
        return rows

    def find_all_receiver(self) -> List[dict]:
        rows = self.db.query("SELECT * FROM bundle_receiver")
        for row in rows:
            row["bundle"] = json.loads(row["bundle"])
        return rows
    
    # ------------------------ UPDATE STATUS ------------------------
    def update_status_receiver(self, hash_str: str, status: bool):
        sql = "UPDATE bundle_receiver SET status = ? WHERE hash = ?"
        self.db.execute(sql, (int(status), hash_str))

    def update_status_send(self, hash_str: str, status: bool):
        sql = "UPDATE bundle_send SET status = ? WHERE hash = ?"
        self.db.execute(sql, (int(status), hash_str))

    def close(self):
        self.db.close()
