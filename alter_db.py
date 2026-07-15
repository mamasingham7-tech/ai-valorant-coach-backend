import sqlite3
import json

db_path = "dev.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN preferences JSON DEFAULT '{}'")
    conn.commit()
    print("Column added successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
