import sqlite3
import datetime

DB_NAME = "twotwo.db"
today = datetime.date.today().isoformat()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d, answer FROM questions WHERE date=?", (today,))
rows = cursor.fetchall()

if not rows:
    print("No questions found for today.")
else:
    for r in rows:
        print(f"ID: {r[0]}")
        print(f"Q: {r[1]}")
        print(f"A: {r[2]}, B: {r[3]}, C: {r[4]}, D: {r[5]}")
        print(f"Answer: {r[6]}")
        print("-" * 40)

conn.close()
