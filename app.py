"""
app.py — Student Result Management System (SRMS)
----------------------------------------------------------------------------
A multi-page desktop-style app built with Streamlit + SQLite, styled after
a classic WinForms admin tool: Login/Register screen, then a top navbar
(Course / Student / Result / View Student Results / Logout) where each
button switches the visible page — all backed by one shared database
(db.py) and AI-generated result remarks (ai_feedback.py).

RUN WITH:
    python app.py
(this relaunches itself under `streamlit run` automatically)
"""

import os
import sys
import streamlit as st
import streamlit.runtime as st_runtime
import pandas as pd

import db
import ai_feedback

# ---------------------------------------------------------------------
# Allow `python app.py` to work directly
# ---------------------------------------------------------------------
if not st_runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", os.path.abspath(__file__), "--server.headless=false"]
    sys.exit(stcli.main())

st.set_page_config(page_title="Student Result Management System", page_icon="📘", layout="wide")
db.init_db()

# ---------------------------------------------------------------------
# STYLING
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #F3F6FA; }

.topbar {
    background: #12294D;
    padding: 14px 24px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 16px;
    text-align: center;
}

.page-header {
    background: #F5A623;
    color: #1B1B1B;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 18px;
}

div[data-testid="stHorizontalBlock"] > div .stButton button {
    background: #16345C;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 0;
    font-weight: 600;
}
div[data-testid="stHorizontalBlock"] > div .stButton button:hover {
    background: #21508C;
    color: white;
}

.metric-box {
    background: #EA5D2A;
    color: white;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    font-size: 20px;
    font-weight: 600;
}

/* ---------- Auth screens (login / register) ---------- */
.auth-wrap {
    display: flex;
    max-width: 900px;
    margin: 40px auto;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(18,41,77,0.18);
}
.auth-side {
    background: linear-gradient(160deg, #12294D 0%, #1F3E70 100%);
    color: #EAF0FB;
    flex: 0 0 40%;
    padding: 48px 34px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.auth-side h2 {
    font-family: 'Poppins', sans-serif;
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 12px;
}
.auth-side p {
    font-size: 14px;
    line-height: 1.6;
    color: #C4D2EC;
}
.auth-form {
    background: white;
    flex: 1;
    padding: 48px 40px;
}
.auth-title {
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #12294D;
    margin-bottom: 4px;
}
.auth-subtitle {
    font-size: 13.5px;
    color: #7A8399;
    margin-bottom: 26px;
}
.auth-form div[data-testid="stTextInput"] input {
    border-radius: 8px;
    border: 1px solid #DDE3EE;
    padding: 10px 12px;
}
.auth-form .stButton button {
    background: #12294D;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 0;
    font-weight: 600;
    font-size: 15px;
}
.auth-form .stButton button:hover {
    background: #1F3E70;
}
.auth-form .stFormSubmitButton button {
    background: #12294D;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 0;
    font-weight: 600;
    font-size: 15px;
}
.auth-form .stFormSubmitButton button:hover {
    background: #1F3E70;
}
.auth-link-btn button {
    background: transparent !important;
    color: #12294D !important;
    border: 1px solid #DDE3EE !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_email" not in st.session_state:
    st.session_state.user_email = None


def go(page):
    st.session_state.page = page
    st.rerun()


# =======================================================================
# LOGIN PAGE
# =======================================================================
def login_page():
    st.write("")
    c1, c2, c3 = st.columns([1, 2.2, 1])
    with c2:
        left, right = st.columns([1, 1.3], gap="small")
        with left:
            st.markdown("""
            <div class="auth-side" style="border-radius: 18px 0 0 18px; min-height: 460px;">
                <h2>Student Result<br>Management System</h2>
                <p>Manage courses, students, and results from one place —
                with AI-assisted feedback for every result you record.</p>
            </div>
            """, unsafe_allow_html=True)
        with right:
            st.markdown('<div class="auth-form" style="border-radius: 0 18px 18px 0; min-height: 460px;">', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Log in to continue to your dashboard</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("Email address")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

            if submitted:
                user = db.verify_login(email.strip(), password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    go("home")
                else:
                    st.error("Invalid email or password.")

            st.markdown('<div class="auth-link-btn">', unsafe_allow_html=True)
            if st.button("Create a new account", use_container_width=True):
                go("register")
            st.markdown('</div></div>', unsafe_allow_html=True)


# =======================================================================
# REGISTER PAGE
# =======================================================================
def register_page():
    st.write("")
    c1, c2, c3 = st.columns([0.6, 2.6, 0.6])
    with c2:
        left, right = st.columns([1, 1.5], gap="small")
        with left:
            st.markdown("""
            <div class="auth-side" style="border-radius: 18px 0 0 18px; min-height: 560px;">
                <h2>Create your<br>account</h2>
                <p>Set up access to manage courses, students, and results —
                takes less than a minute.</p>
            </div>
            """, unsafe_allow_html=True)
        with right:
            st.markdown('<div class="auth-form" style="border-radius: 0 18px 18px 0; min-height: 560px;">', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Register</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Fill in your details to get started</div>', unsafe_allow_html=True)

            with st.form("register_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                first_name = col1.text_input("First name")
                last_name = col2.text_input("Last name")
                contact = col1.text_input("Contact no.")
                email = col2.text_input("Email")
                sec_q = st.selectbox("Security question", ["Your first pet's name", "Your birth city", "Your favorite teacher"])
                answer = st.text_input("Answer")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                agree = st.checkbox("I agree to the terms & conditions")

                submitted = st.form_submit_button("Register now", type="primary", use_container_width=True)

            if submitted:
                missing = []
                if not first_name.strip():
                    missing.append("First name")
                if not email.strip():
                    missing.append("Email")
                if not password:
                    missing.append("Password")
                if missing:
                    st.error(f"Missing required field(s): {', '.join(missing)}")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif not agree:
                    st.error("Please accept the terms & conditions.")
                elif db.get_user_by_email(email.strip()):
                    st.error("An account with this email already exists.")
                else:
                    db.create_user(first_name, last_name, contact, email.strip(), sec_q, answer, password)
                    st.success("Registered! You can log in now.")
                    go("login")

            st.markdown('<div class="auth-link-btn">', unsafe_allow_html=True)
            if st.button("Back to login", use_container_width=True):
                go("login")
            st.markdown('</div></div>', unsafe_allow_html=True)


# =======================================================================
# NAVBAR (shown on every page once logged in)
# =======================================================================
def navbar():
    st.markdown('<div class="topbar">Student Result Management System</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    labels = ["Home", "Course", "Student", "Result", "View Student Results", "Logout"]
    targets = ["home", "course", "student", "result", "view_results", "logout"]
    for col, label, target in zip(cols, labels, targets):
        with col:
            if st.button(label, use_container_width=True, key=f"nav_{target}"):
                if target == "logout":
                    st.session_state.logged_in = False
                    st.session_state.user_email = None
                    go("login")
                else:
                    go(target)


# =======================================================================
# HOME PAGE
# =======================================================================
def home_page():
    navbar()
    total_courses = len(db.list_courses())
    total_students = len(db.list_students())
    total_results = len(db.list_results())

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-box">Total Courses<br>[{total_courses}]</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box">Total Students<br>[{total_students}]</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box">Total Results<br>[{total_results}]</div>', unsafe_allow_html=True)

    st.write("")
    st.info("Use the navbar above to manage courses, students, and results.")


# =======================================================================
# COURSE PAGE
# =======================================================================
def course_page():
    navbar()
    st.markdown('<div class="page-header">Manage Course Details</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.3])
    with left:
        name = st.text_input("Course Name")
        duration = st.text_input("Duration")
        charges = st.number_input("Charges", min_value=0.0, step=100.0)
        description = st.text_area("Description")

        b1, b2, b3, b4 = st.columns(4)
        if b1.button("Save", use_container_width=True):
            if name.strip():
                db.save_course(name.strip(), duration, charges, description)
                st.success(f"Course '{name}' saved.")
                st.rerun()
            else:
                st.error("Course name is required.")
        if b2.button("Clear", use_container_width=True):
            st.rerun()

    with right:
        search = st.text_input("Search course by name")
        rows = db.list_courses(search)
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Name", "Duration", "Charges", "Description"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            del_id = st.selectbox("Select course ID to delete", df["ID"])
            if st.button("Delete selected course"):
                db.delete_course(int(del_id))
                st.rerun()
        else:
            st.caption("No courses yet.")


# =======================================================================
# STUDENT PAGE
# =======================================================================
def student_page():
    navbar()
    st.markdown('<div class="page-header">Manage Student Details</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.2])
    with left:
        c1, c2 = st.columns(2)
        roll_no = c1.text_input("Roll No.")
        dob = c2.date_input("D.O.B", value=None, format="YYYY-MM-DD")
        name = c1.text_input("Name")
        contact = c2.text_input("Contact")
        email = c1.text_input("Email")
        admission = c2.date_input("Admission date", value=None, format="YYYY-MM-DD")
        gender = c1.selectbox("Gender", ["Female", "Male", "Other"])

        courses = db.list_courses()
        course_map = {c[1]: c[0] for c in courses}
        course_name = c2.selectbox("Course", ["Select"] + list(course_map.keys()))

        c1, c2, c3 = st.columns(3)
        state = c1.text_input("State")
        city = c2.text_input("City")
        pin = c3.text_input("Pin")
        address = st.text_area("Address")

        b1, b2 = st.columns(2)
        if b1.button("Save", use_container_width=True):
            if roll_no.strip() and name.strip():
                course_id = course_map.get(course_name)
                db.save_student(
                    roll_no.strip(), name.strip(), str(dob) if dob else "", contact,
                    email, str(admission) if admission else "", gender,
                    course_id, state, city, pin, address,
                )
                st.success(f"Student '{name}' saved.")
                st.rerun()
            else:
                st.error("Roll No. and Name are required.")
        if b2.button("Clear", use_container_width=True):
            st.rerun()

    with right:
        search = st.text_input("Search by Roll No. or Name")
        rows = db.list_students(search)
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Roll No.", "Name", "Email", "Gender", "D.O.B"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            del_id = st.selectbox("Select student ID to delete", df["ID"])
            if st.button("Delete selected student"):
                db.delete_student(int(del_id))
                st.rerun()
        else:
            st.caption("No students yet.")


# =======================================================================
# RESULT PAGE (with AI-generated remark)
# =======================================================================
def result_page():
    navbar()
    st.markdown('<div class="page-header">Add Student Results</div>', unsafe_allow_html=True)

    roll_numbers = db.all_roll_numbers()
    if not roll_numbers:
        st.warning("Add a student first on the Student page.")
        return

    left, right = st.columns([1.3, 1])
    with left:
        roll_no = st.selectbox("Select Student (Roll No.)", roll_numbers)
        student = db.get_student_by_roll(roll_no)
        # students columns: id, roll_no, name, dob, contact, email, admission_date,
        #                    gender, course_id, state, city, pin, address
        student_id, _, name = student[0], student[1], student[2]
        course_id = student[8]
        course_row = db.get_course(course_id) if course_id else None
        course_name = course_row[1] if course_row else "—"

        st.text_input("Name", value=name, disabled=True)
        st.text_input("Course", value=course_name, disabled=True)

        marks_obtained = st.number_input("Marks Obtained", min_value=0.0, step=1.0)
        full_marks = st.number_input("Full Marks", min_value=1.0, value=100.0, step=1.0)

        smart_available = bool(os.environ.get("OPENAI_API_KEY"))
        use_ai = st.toggle(
            "AI-generated remark",
            value=smart_available,
            disabled=not smart_available,
            help="Set OPENAI_API_KEY to enable." if not smart_available else "Remark will be written by AI.",
        )

        if st.button("Submit", type="primary", use_container_width=True):
            percentage = round((marks_obtained / full_marks) * 100, 2) if full_marks else 0
            with st.spinner("Generating remark..."):
                if use_ai:
                    remark = ai_feedback.generate_remark(name, course_name, marks_obtained, full_marks, percentage)
                else:
                    remark = ai_feedback.generate_remark_rule_based(name, percentage)
            db.save_result(student_id, marks_obtained, full_marks, remark)
            st.success(f"Result saved — {percentage}%")
            st.info(remark)

    with right:
        st.image(
            "https://api.dicebear.com/7.x/icons/svg?icon=mortarboard&backgroundColor=1B2A4E",
            width=180,
        )


# =======================================================================
# VIEW RESULTS PAGE
# =======================================================================
def view_results_page():
    navbar()
    st.markdown('<div class="page-header">View Student Results</div>', unsafe_allow_html=True)

    search = st.text_input("Search By Roll No.")
    rows = db.list_results(search)

    if rows:
        df = pd.DataFrame(
            rows,
            columns=["Result ID", "Roll No", "Name", "Course", "Marks Obtained", "Total Marks", "Percentage", "Remark"],
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        del_id = st.selectbox("Select result ID to delete", df["Result ID"])
        if st.button("Delete", type="primary"):
            db.delete_result(int(del_id))
            st.rerun()
    else:
        st.caption("No results found.")


# =======================================================================
# ROUTER
# =======================================================================
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        register_page()
    else:
        login_page()
else:
    page = st.session_state.page
    if page == "home":
        home_page()
    elif page == "course":
        course_page()
    elif page == "student":
        student_page()
    elif page == "result":
        result_page()
    elif page == "view_results":
        view_results_page()
    else:
        home_page()