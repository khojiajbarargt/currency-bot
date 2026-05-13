import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("bot.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            from_cur TEXT,
            result REAL,
            to_cur TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_conversion(user_id, amount, from_cur, result, to_cur):
    conn = sqlite3.connect("bot.db")
    conn.execute(
        "INSERT INTO history (user_id, amount, from_cur, result, to_cur, date) VALUES (?,?,?,?,?,?)",
        (user_id, amount, from_cur, result, to_cur, datetime.now().strftime("%d.%m.%Y %H:%M"))
    )
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    conn = sqlite3.connect("bot.db")
    rows = conn.execute(
        "SELECT amount, from_cur, result, to_cur, date FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return rows