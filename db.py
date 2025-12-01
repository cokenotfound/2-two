import sqlite3
from sqlite3 import Error

DB_NAME = "2two.db"

# -------------------------
# Create DB connection
# -------------------------
def get_connection():
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        return conn
    except Error as e:
        print("Error connecting to DB:", e)
        return None

# -------------------------
# Create tables
# -------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        answer TEXT,
        explanation TEXT
    )
    """)
    
    # User answers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        choice TEXT,
        correct INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(question_id) REFERENCES questions(id)
    )
    """)
    
    conn.commit()
    conn.close()

# -------------------------
# Save questions
# -------------------------
def save_questions(date, questions, overwrite=False):
    conn = get_connection()
    cursor = conn.cursor()

    if overwrite:
        # Delete old questions for this date
        cursor.execute("DELETE FROM questions WHERE date=?", (date,))
    
    for q in questions:
        # Check if question ID exists in the dictionary before accessing
        cursor.execute("""
        INSERT INTO questions 
        (date, question, option_a, option_b, option_c, option_d, answer, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            q["question"],
            q["options"].get("A", ""),
            q["options"].get("B", ""),
            q["options"].get("C", ""),
            q["options"].get("D", ""),
            q["answer"],
            q["explanation"]
        ))
    conn.commit()
    conn.close()


# -------------------------
# Fetch questions by date
# -------------------------
def get_questions_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE date=?", (date,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------------
# Save user answer
# -------------------------
def save_user_answer(question_id, choice, correct):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_answers (question_id, choice, correct)
    VALUES (?, ?, ?)
    """, (question_id, choice, int(correct)))
    conn.commit()
    conn.close()

# -------------------------
# Test DB
# -------------------------
if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")