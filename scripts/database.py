import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('tutor_progress.db')
    c = conn.cursor()
    # Stores every interaction for the weekly report
    c.execute('''CREATE TABLE IF NOT EXISTS progress 
                 (timestamp TEXT, skill TEXT, correct INTEGER, latency REAL)''')
    conn.commit()
    conn.close()

def log_attempt(skill, is_correct, latency):
    conn = sqlite3.connect('tutor_progress.db')
    c = conn.cursor()
    c.execute("INSERT INTO progress VALUES (?, ?, ?, ?)", 
              (datetime.datetime.now().isoformat(), skill, 1 if is_correct else 0, latency))
    conn.commit()
    conn.close()