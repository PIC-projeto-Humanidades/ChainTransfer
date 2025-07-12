from typing import List
from pathlib import Path
from database.SQLExecutor import SQLExecutor
from pathlib import Path

# Caminho absoluto para o banco de dados
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "dtn.db"

class FilesReceiverRepository:
    def __init__(self):
        self.db = SQLExecutor(str(DB_PATH))

    # ------------------------ INSERT ------------------------
    def insert_file(self, hash_str: str, file_name: str):
        sql = "INSERT INTO files_receiver (hash, file_name) VALUES (?, ?)"
        self.db.execute(sql, (hash_str, file_name))

    # ------------------------ FIND BY HASH ------------------------
    def find_by_hash(self, hash_str: str) -> List[dict]:
        sql = "SELECT * FROM files_receiver WHERE hash = ?"
        return self.db.query(sql, (hash_str,))

    # ------------------------ FIND BY FILE NAME ------------------------
    def find_by_file_name(self, file_name: str) -> List[dict]:
        sql = "SELECT * FROM files_receiver WHERE file_name = ?"
        return self.db.query(sql, (file_name,))

    # ------------------------ FIND ALL ------------------------
    def find_all(self) -> List[dict]:
        sql = "SELECT * FROM files_receiver"
        return self.db.query(sql)

    def close(self):
        self.db.close()
