import sqlite3
import pandas as pd
import os

DB_PATH = "data/placemate.db"
CSV_PATH = "data/processed/cleaned_student_placement_data.csv"

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# DROP TABLES (CLEAN START)
# -----------------------------
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS predictions")

# -----------------------------
# STUDENTS TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    student_name TEXT,
    cgpa REAL,
    coding_skill INTEGER,
    communication_skill INTEGER,
    aptitude_skill INTEGER,
    problem_solving INTEGER,
    projects_count INTEGER,
    internship_count INTEGER,
    internship_company_level INTEGER,
    certification_count INTEGER,
    certification_company_level INTEGER,
    technical_skills INTEGER,
    tools_known INTEGER,
    placement_probability REAL,
    placement_status TEXT
)
""")

# -----------------------------
# PREDICTIONS TABLE (FIXED)
# -----------------------------
cursor.execute("""
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    prediction TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv(CSV_PATH)

df.rename(columns={
    "Student_name": "student_name"
}, inplace=True)

df["student_id"] = df["student_id"].astype(str).str.strip().str.upper()

df.to_sql("students", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("✅ Database setup completed successfully")
