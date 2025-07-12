import sqlite3
from typing import Any, List, Tuple, Optional
from pathlib import Path

class SQLExecutor:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        """Executa um SQL genérico (INSERT, UPDATE, DELETE, etc)."""
        self.cursor.execute(sql, params or ())
        self.conn.commit()

    def executemany(self, sql: str, param_list: List[Tuple[Any, ...]]) -> None:
        """Executa comandos com muitos parâmetros."""
        self.cursor.executemany(sql, param_list)
        self.conn.commit()

    def query(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[dict]:
        """Executa SELECT e retorna uma lista de dicionários."""
        self.cursor.execute(sql, params or ())
        return [dict(row) for row in self.cursor.fetchall()]

    def fetch_one(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[dict]:
        """Executa SELECT e retorna apenas uma linha como dicionário."""
        self.cursor.execute(sql, params or ())
        result = self.cursor.fetchone()
        return dict(result) if result else None

    def close(self):
        """Fecha a conexão."""
        self.cursor.close()
        self.conn.close()
