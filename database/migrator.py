import sqlite3
from pathlib import Path

# Caminho absoluto para o banco de dados
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "dtn.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bundle_send (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        hash_secondary TEXT,
        bundle TEXT NOT NULL,
        status BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bundle_receiver (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        bundle TEXT NOT NULL,
        status BOOLEAN NOT NULL DEFAULT 0,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files_receiver (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT NOT NULL,
        file_name TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Tabelas com coluna 'status' criadas/verificadas com sucesso.")
