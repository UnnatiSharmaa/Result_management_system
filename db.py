"""
db.py — Shared database layer for Student Result Management System (SRMS)
----------------------------------------------------------------------------
All tables and CRUD functions live here so every page in app.py talks to
the same single source of truth: srms.db (SQLite).
"""

import sqlite3

DB_PATH = "srms.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            contact TEXT,
            email TEXT UNIQUE NOT NULL,
            security_question TEXT,
            answer TEXT,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration TEXT,
            charges REAL,
            description TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            dob TEXT,
            contact TEXT,
            email TEXT,
            admission_date TEXT,
            gender TEXT,
            course_id INTEGER,
            state TEXT,
            city TEXT,
            pin TEXT,
            address TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            marks_obtained REAL,
            full_marks REAL,
            percentage REAL,
            remark TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# USERS (login/register)
# ---------------------------------------------------------------------
def create_user(first_name, last_name, contact, email, sec_q, answer, password):
    conn = get_conn()
    conn.execute(
        """INSERT INTO users (first_name, last_name, contact, email, security_question, answer, password)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (first_name, last_name, contact, email, sec_q, answer, password),
    )
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def verify_login(email, password):
    row = get_user_by_email(email)
    if row and row[7] == password:
        return row
    return None


# ---------------------------------------------------------------------
# COURSES
# ---------------------------------------------------------------------
def save_course(name, duration, charges, description):
    conn = get_conn()
    conn.execute(
        "INSERT INTO courses (name, duration, charges, description) VALUES (?, ?, ?, ?)",
        (name, duration, charges, description),
    )
    conn.commit()
    conn.close()


def update_course(course_id, name, duration, charges, description):
    conn = get_conn()
    conn.execute(
        "UPDATE courses SET name=?, duration=?, charges=?, description=? WHERE id=?",
        (name, duration, charges, description, course_id),
    )
    conn.commit()
    conn.close()


def delete_course(course_id):
    conn = get_conn()
    conn.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()


def list_courses(search=""):
    conn = get_conn()
    if search:
        rows = conn.execute(
            "SELECT id, name, duration, charges, description FROM courses WHERE name LIKE ?",
            (f"%{search}%",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, name, duration, charges, description FROM courses"
        ).fetchall()
    conn.close()
    return rows


def get_course(course_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------
# STUDENTS
# ---------------------------------------------------------------------
def save_student(roll_no, name, dob, contact, email, admission_date, gender,
                  course_id, state, city, pin, address):
    conn = get_conn()
    conn.execute(
        """INSERT INTO students
           (roll_no, name, dob, contact, email, admission_date, gender, course_id, state, city, pin, address)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (roll_no, name, dob, contact, email, admission_date, gender, course_id, state, city, pin, address),
    )
    conn.commit()
    conn.close()


def update_student(student_id, **fields):
    conn = get_conn()
    cols = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [student_id]
    conn.execute(f"UPDATE students SET {cols} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_conn()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()


def list_students(search=""):
    conn = get_conn()
    if search:
        rows = conn.execute(
            "SELECT id, roll_no, name, email, gender, dob FROM students WHERE roll_no LIKE ? OR name LIKE ?",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT id, roll_no, name, email, gender, dob FROM students").fetchall()
    conn.close()
    return rows


def get_student_by_roll(roll_no):
    conn = get_conn()
    row = conn.execute("SELECT * FROM students WHERE roll_no=?", (roll_no,)).fetchone()
    conn.close()
    return row


def all_roll_numbers():
    conn = get_conn()
    rows = conn.execute("SELECT roll_no FROM students ORDER BY roll_no").fetchall()
    conn.close()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------
def save_result(student_id, marks_obtained, full_marks, remark):
    percentage = round((marks_obtained / full_marks) * 100, 2) if full_marks else 0
    conn = get_conn()
    conn.execute(
        "INSERT INTO results (student_id, marks_obtained, full_marks, percentage, remark) VALUES (?, ?, ?, ?, ?)",
        (student_id, marks_obtained, full_marks, percentage, remark),
    )
    conn.commit()
    conn.close()
    return percentage


def delete_result(result_id):
    conn = get_conn()
    conn.execute("DELETE FROM results WHERE id=?", (result_id,))
    conn.commit()
    conn.close()


def list_results(search_roll=""):
    conn = get_conn()
    query = """
        SELECT r.id, s.roll_no, s.name, c.name, r.marks_obtained, r.full_marks, r.percentage, r.remark
        FROM results r
        JOIN students s ON r.student_id = s.id
        LEFT JOIN courses c ON s.course_id = c.id
    """
    if search_roll:
        query += " WHERE s.roll_no LIKE ?"
        rows = conn.execute(query, (f"%{search_roll}%",)).fetchall()
    else:
        rows = conn.execute(query).fetchall()
    conn.close()
    return rows
