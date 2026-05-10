import sqlite3

DB_PATH = "data/placemate.db"

# -----------------------------
# Find Student (FIXED)
# -----------------------------
def find_student(student_id):
    student_id = student_id.strip().upper()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM students
    WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()
    conn.close()

    if student is None:
        print("❌ Student not found. Please register first.")
        return None

    return student
