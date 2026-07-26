import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'finance.db')

def init_db():
    """Upgraded Database Schema with automatic table migration."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Base Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL
        )
    ''')
    
    # 2. Auto-Migration Layer: Automatically adds new columns to existing database
    new_columns = [
        ("timestamp", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("voice_confidence", "REAL DEFAULT 1.0"),
        ("edited_after_entry", "INTEGER DEFAULT 0"),
        ("tags", "TEXT DEFAULT ''"),
        ("recurring_flag", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            # Column already exists
            pass

    # 3. Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_setting(key, default_val=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default_val

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

def add_transaction(date, amount, category, description, trans_type, voice_confidence=1.0, edited=0, tags="", recurring=0):
    """Inserts enhanced transaction record into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO transactions (date, amount, category, description, type, timestamp, voice_confidence, edited_after_entry, tags, recurring_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, amount, category, description, trans_type, timestamp, voice_confidence, edited, tags, recurring))
    conn.commit()
    conn.close()

def get_all_transactions():
    """Retrieves all records from transactions table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, date, amount, category, description, type, timestamp, voice_confidence, edited_after_entry, tags, recurring_flag 
        FROM transactions ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_transaction(trans_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
    conn.commit()
    conn.close()

def delete_all_transactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions')
    conn.commit()
    conn.close()