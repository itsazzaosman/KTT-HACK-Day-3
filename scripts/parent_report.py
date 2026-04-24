import sqlite3
import os
from database import cipher_suite

def generate_report():
    db_path = 'tutor_progress.db'
    if not os.path.exists(db_path):
        print("⚠️ No data found! Play a few games in demo.py first.")
        return

    # 1. Read the Encrypted Data
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT encrypted_skill, encrypted_correct FROM progress")
        rows = c.fetchall()
    except sqlite3.OperationalError:
        print("⚠️ Database schema mismatch. Please delete tutor_progress.db and try again.")
        return
    finally:
        conn.close()

    if not rows:
        print("⚠️ No data to report yet.")
        return

    # 2. Decrypt and Aggregate the Data manually
    stats_dict = {}
    for enc_skill, enc_correct in rows:
        # Decrypting back to normal text
        skill = cipher_suite.decrypt(enc_skill).decode()
        correct = int(cipher_suite.decrypt(enc_correct).decode())
        
        if skill not in stats_dict:
            stats_dict[skill] = {"total": 0, "correct": 0}
        stats_dict[skill]["total"] += 1
        stats_dict[skill]["correct"] += correct

    # Convert to a list for the HTML generator
    stats = [(skill, data["total"], data["correct"]) for skill, data in stats_dict.items()]

    # 3. Build the Visual HTML Report
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Weekly Progress Report</title>
        <style>
            body { font-family: sans-serif; text-align: center; background-color: #f4f4f9; padding: 20px; }
            .card { background: white; border-radius: 15px; padding: 30px; max-width: 400px; margin: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            h1 { color: #333; font-size: 24px; margin-bottom: 5px; }
            .subtitle { color: #777; font-size: 14px; margin-bottom: 20px; }
            .skill { margin: 20px 0; font-size: 28px; text-align: left; display: flex; align-items: center; }
            .icon { width: 50px; text-align: center; margin-right: 15px; }
            .bars { flex-grow: 1; letter-spacing: 2px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📊 Learner Progress</h1>
            <div class="subtitle">Weekly Visual Summary (Encrypted)</div>
            <hr style="border: 1px solid #eee;">
    """

    for skill, total, correct in stats:
        wrong = total - correct
        icons = {
            "counting": "🍎", "addition": "➕", "subtraction": "➖", 
            "number_sense": "⚖️", "word_problems": "📖"
        }
        icon = icons.get(skill, "📝")
        correct_bar = "🟩" * correct
        wrong_bar = "🟥" * wrong

        html_content += f"""
            <div class="skill">
                <div class="icon">{icon}</div>
                <div class="bars">{correct_bar}{wrong_bar}</div>
            </div>
        """

    html_content += """
            <hr style="border: 1px solid #eee; margin-top: 20px;">
            <h2 style="font-size: 40px; margin: 10px 0;">⭐</h2>
        </div>
    </body>
    </html>
    """

    report_file = "parent_report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Encrypted Parent Report generated successfully: {report_file}")

if __name__ == "__main__":
    generate_report()