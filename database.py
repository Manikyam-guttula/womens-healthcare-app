import sqlite3
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    # Table for logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            cycle_day INTEGER,
            symptom TEXT,
            severity INTEGER,
            mood TEXT,
            notes TEXT
        )
    ''')
    # Table for security PIN
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security (
            id INTEGER PRIMARY KEY,
            pin_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def set_pin(pin):
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    hashed = hash_pin(pin)
    cursor.execute("INSERT OR REPLACE INTO security (id, pin_hash) VALUES (1, ?)", (hashed,))
    conn.commit()
    conn.close()

def verify_pin(pin):
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pin_hash FROM security WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None  # No PIN set yet
    return row[0] == hash_pin(pin)

def add_log(cycle_day, symptom, severity, mood, notes):
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO logs (date, cycle_day, symptom, severity, mood, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (date_str, cycle_day, symptom, severity, mood, notes)
    )
    conn.commit()
    conn.close()

def get_logs():
    import pandas as pd
    conn = sqlite3.connect('health_data.db')
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df