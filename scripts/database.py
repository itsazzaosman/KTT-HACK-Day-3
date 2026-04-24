import sqlite3
import datetime
import os
from cryptography.fernet import Fernet

# 1. Setup Encryption Key (Creates a local .key file)
KEY_FILE = "tutor.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(KEY_FILE, "rb") as f:
        return f.read()
# Initialize the cipher suite with the loaded key
cipher_suite = Fernet(load_key())

# 2. Database Functions
def init_db():
    conn = sqlite3.connect('tutor_progress.db')
    c = conn.cursor()
    # We store the encrypted strings as bytes
    c.execute('''CREATE TABLE IF NOT EXISTS progress 
                 (timestamp TEXT, encrypted_skill bytes, encrypted_correct bytes, latency REAL)''')
    conn.commit()
    conn.close()

def log_attempt(skill, is_correct, latency):
    conn = sqlite3.connect('tutor_progress.db')
    c = conn.cursor()
    
    # Encrypt the sensitive data before inserting
    enc_skill = cipher_suite.encrypt(skill.encode())
    enc_correct = cipher_suite.encrypt(str(1 if is_correct else 0).encode())
    
    c.execute("INSERT INTO progress VALUES (?, ?, ?, ?)", 
              (datetime.datetime.now().isoformat(), enc_skill, enc_correct, latency))
    conn.commit()
    conn.close()