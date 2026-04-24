import sqlite3

# Connect directly to the database without the decryption key
conn = sqlite3.connect('tutor_progress.db')
cursor = conn.cursor()

print("\n🔒 RAW DATABASE CONTENTS (HACKER VIEW):")
for row in cursor.execute("SELECT * FROM progress LIMIT 2"):
    print(f"Timestamp: {row[0]}")
    print(f"Skill: {row[1]}")
    print(f"Score: {row[2]}\n")