from google.genai import types
import streamlit as st
import pandas as pd
from google import genai
from pathlib import Path
from datetime import date
import time
from supabase import create_client

st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide"
)

DATA = Path("data")
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_PUBLISHABLE_KEY"]

if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

def load_csv(filename):
    path = DATA / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

semesters = load_csv("semesters.csv")
courses = load_csv("courses.csv")
calendar = load_csv("academic_calendar.csv")
assessments = load_csv("assessments.csv")
scores = load_csv("scores.csv")

st.sidebar.title("🎓 Degree OS")

pages = [
    "Dashboard",
    "Semesters 1-8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin"
]

page = st.sidebar.radio("Navigation", pages)
# Supabase Authentication
db = st.session_state.supabase

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.sidebar.subheader("🔐 Account Login")

    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            try:
                response = db.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                st.session_state.user = response.user
                st.sidebar.success("Login successful!")
                st.rerun()

            except Exception as e:
                st.sidebar.error(f"Login failed: {e}")

else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        db.auth.sign_out()
        st.session_state.user = None
        st.rerun()

# Dashboard
if page == "Dashboard":

    st.title("🎓 My Engineering Degree OS")
    st.write("Your personal engineering degree command center.")

    current_semester = 3

    total_credits = semesters["total_credits"].sum() if not semesters.empty else 0
    completed_credits = semesters["completed_credits"].sum() if not semesters.empty else 0

    completion = (
        completed_credits / total_credits * 100
        if total_credits else 0
    )

    st.subheader("Degree Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Current Semester", current_semester)
    col2.metric("Degree Completion", f"{completion:.1f}%")
    col3.metric("Completed Credits", int(completed_credits))
    col4.metric("Total Credits", int(total_credits))

    st.progress(completion / 100)

    # Upcoming assessment
    st.subheader("📅 Upcoming Assessment")

    if not assessments.empty:
        assessments["date"] = pd.to_datetime(
            assessments["date"], errors="coerce"
        )

        upcoming = assessments[
            assessments["date"] >= pd.Timestamp(date.today())
        ].sort_values("date")

        if not upcoming.empty:
            next_exam = upcoming.iloc[0]

            st.info(
                f"{next_exam['course_code']} - "
                f"{next_exam['assessment_type']} "
                f"on {next_exam['date'].strftime('%d %b %Y')}"
            )
        else:
            st.write("No upcoming assessments found.")
    else:
        st.write("Assessment data is unavailable.")

    # Upcoming holiday
    st.subheader("🌴 Next Holiday")

    if not calendar.empty:
        calendar["date"] = pd.to_datetime(
            calendar["date"], errors="coerce"
        )

        holidays = calendar[
            calendar["event_type"].str.lower().isin(
                ["holiday", "leave"]
            )
            & (calendar["date"] >= pd.Timestamp(date.today()))
        ].sort_values("date")

        if not holidays.empty:
            holiday = holidays.iloc[0]

            st.success(
                f"{holiday['title']} - "
                f"{holiday['date'].strftime('%d %b %Y')}"
            )
        else:
            st.write("No upcoming holidays found.")
    else:
        st.write("Calendar data is unavailable.")

    # Score summary
    st.subheader("📊 Score Summary")

    if not scores.empty:
        total_score = scores["score"].sum()
        max_score = scores["max_marks"].sum()

        percentage = (
            total_score / max_score * 100
            if max_score else 0
        )

        st.metric(
            "Prototype Score Percentage",
            f"{percentage:.2f}%"
        )
    else:
        st.write("No score data available.")

    # Semester progress chart
    st.subheader("📈 Semester Progress")

    if not semesters.empty:
        chart_data = semesters[
            ["semester", "completed_credits", "total_credits"]
        ].copy()

        chart_data["Progress (%)"] = (
            chart_data["completed_credits"]
            / chart_data["total_credits"] * 100
        )

        chart_data["Semester"] = (
            "Semester " + chart_data["semester"].astype(str)
        )

        st.bar_chart(
            chart_data.set_index("Semester")["Progress (%)"]
        )

# Semesters 1-8 page
elif page == "Semesters 1-8":
    st.title("Semesters 1–8")

    if semesters.empty:
        st.warning("Semester data is unavailable.")
    else:
        for _, sem in semesters.iterrows():
            with st.expander(f"Semester {int(sem['semester'])}"):
                st.write("Status:", sem["status"])
                st.write("Total Credits:", sem["total_credits"])
                st.write("Completed Credits:", sem["completed_credits"])

                if not courses.empty:
                    sem_courses = courses[
                        courses["semester"] == sem["semester"]
                    ]

                    st.dataframe(
                        sem_courses,
                        use_container_width=True
                    )
# Courses & Syllabus page
elif page == "Courses & Syllabus":
    st.title("Courses & Syllabus")

    if courses.empty:
        st.warning("Course data is unavailable.")
    else:
        sem_no = st.selectbox(
            "Select Semester",
            sorted(courses["semester"].unique())
        )

        sem_courses = courses[courses["semester"] == sem_no]

        st.dataframe(sem_courses, width="stretch")

        st.subheader("Course Syllabus")

        course = st.selectbox(
            "Select Course",
            sem_courses["course_name"].tolist()
        )

        syllabus = sem_courses[
            sem_courses["course_name"] == course
        ]["syllabus"].iloc[0]

        st.write(syllabus)
# University Syllabus page
elif page == "University Syllabus":
    st.title("University Syllabus")

    st.info(
        "Add your official university syllabus PDF or link here."
    )

    st.subheader("Semester-wise Syllabus")

    if courses.empty:
        st.warning("Course data is unavailable.")
    else:
        sem_no = st.selectbox(
            "Select Semester",
            sorted(courses["semester"].unique()),
            key="university_semester"
        )

        sem_courses = courses[courses["semester"] == sem_no]

        for _, course in sem_courses.iterrows():
            with st.expander(course["course_name"]):
                st.write(course["syllabus"])
# Academic / Leave Calendar page
elif page == "Academic / Leave Calendar":
    st.title("Academic / Leave Calendar")

    if calendar.empty:
        st.warning("Calendar data is unavailable.")
    else:
        calendar["date"] = pd.to_datetime(calendar["date"])

        st.dataframe(calendar, width="stretch")

        st.subheader("Upcoming Events")

        upcoming = calendar[
            calendar["date"] >= pd.Timestamp.today()
        ].sort_values("date")

        if upcoming.empty:
            st.info("No upcoming events found.")
        else:
            for _, event in upcoming.iterrows():
                st.write(
                    f"📅 {event['date'].strftime('%d %b %Y')} — "
                    f"{event['title']} ({event['event_type']})"
                )
# Internal Assessments page
elif page == "Internal Assessments":
    st.title("Internal Assessments")

    if assessments.empty:
        st.warning("Assessment data is unavailable.")
    else:
        sem_no = st.selectbox(
            "Select Semester",
            sorted(assessments["semester"].unique()),
            key="assessment_semester"
        )

        sem_assessments = assessments[
            assessments["semester"] == sem_no
        ].sort_values("date")

        st.dataframe(sem_assessments, width="stretch")

        st.subheader("Assessment Details")

        for _, assessment in sem_assessments.iterrows():
            with st.expander(
                f"{assessment['course_code']} - "
                f"{assessment['assessment_type']}"
            ):
                st.write("Date:", assessment["date"])
                st.write("Maximum Marks:", assessment["max_marks"])
                st.write("Status:", assessment["status"])
# Status Tracker page
elif page == "Status Tracker":
    st.title("Status Tracker")

    if semesters.empty:
        st.warning("Semester data is unavailable.")
    else:
        st.subheader("Semester Progress")

        st.dataframe(
            semesters[
                ["semester", "status", "total_credits", "completed_credits"]
            ],
            width="stretch"
        )

        st.subheader("Overall Degree Progress")

        total_credits = semesters["total_credits"].sum()
        completed_credits = semesters["completed_credits"].sum()

        progress = (
            completed_credits / total_credits
            if total_credits > 0 else 0
        )

        st.progress(progress)
        st.write(f"{progress * 100:.1f}% completed")

        st.subheader("Course Completion")

        if not courses.empty:
            st.dataframe(
                courses[
                    ["semester", "course_code", "course_name", "status"]
                ],
                width="stretch"
            )
# Scorecard page
elif page == "Scorecard":
    st.title("Scorecard")

    if scores.empty:
        st.warning("Score data is unavailable.")
    else:
        sem_no = st.selectbox(
            "Select Semester",
            sorted(scores["semester"].unique()),
            key="score_semester"
        )

        sem_scores = scores[scores["semester"] == sem_no]

        st.dataframe(sem_scores, width="stretch")

        total_score = sem_scores["score"].sum()
        total_marks = sem_scores["max_marks"].sum()

        percentage = (
            total_score / total_marks * 100
            if total_marks > 0 else 0
        )

        st.metric("Total Score", f"{total_score} / {total_marks}")
        st.metric("Score Percentage", f"{percentage:.1f}%")
        st.divider()
    st.subheader("📚 My Saved Scores")

    if st.session_state.user is None:
        st.info("Please log in to save your scores.")
    else:
        with st.form("save_score_form"):
            st.write("Add a new assessment score")

            course_code = st.text_input("Course Code")
            assessment_name = st.text_input("Assessment Name")

            col1, col2 = st.columns(2)

            with col1:
                marks_obtained = st.number_input(
                    "Marks Obtained", min_value=0.0, step=1.0
                )

            with col2:
                total_marks = st.number_input(
                    "Total Marks", min_value=1.0, step=1.0
                )

            exam_date = st.date_input("Exam Date")

            save_score = st.form_submit_button("Save Score")

            if save_score:
                if not course_code.strip() or not assessment_name.strip():
                    st.error("Please enter all required details.")
                elif marks_obtained > total_marks:
                    st.error("Marks obtained cannot exceed total marks.")
                else:
                    try:
                        db.table("scores").insert({
                            "course_code": course_code.strip(),
                            "assessment_name": assessment_name.strip(),
                            "marks_obtained": marks_obtained,
                            "total_marks": total_marks,
                            "exam_date": exam_date.isoformat()
                        }).execute()

                        st.success("Score saved successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Unable to save score: {e}")

        st.write("### Your Saved Scores")

        try:
            response = (
                db.table("scores")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            if response.data:
                st.dataframe(
                    pd.DataFrame(response.data),
                    width="stretch"
                )
            else:
                st.info("You haven't saved any scores yet.")

        except Exception as e:
            st.error(f"Unable to load scores: {e}")
# Plan & Checklist page
elif page == "Plan & Checklist":
    st.title("Plan & Checklist")

    st.subheader("Study Plan")

    tasks = [
        "Review today's topics",
        "Complete pending assignments",
        "Prepare for upcoming internal assessments",
        "Revise completed topics"
    ]

    for task in tasks:
        st.checkbox(task, key=task)

    st.subheader("Weekly Study Goal")

    goal = st.slider(
        "Hours to study this week",
        min_value=1,
        max_value=40,
        value=10
    )

    st.write(f"Your weekly study goal: **{goal} hours**")

# Ask Degree AI page

# Ask Degree AI page
elif page == "Ask Degree AI":
    st.title("Ask Degree AI")
    st.write("Ask questions about your engineering degree.")

    question = st.text_input(
        "Ask a question about your degree"
    )

    if st.button("Ask"):
        if question.strip():
            try:
                api_key = st.secrets.get("GEMINI_API_KEY")

                if not api_key:
                    st.warning("Gemini API key is not configured.")
                else:
                    client = genai.Client(
                        api_key=api_key,
                        http_options=types.HttpOptions(timeout=120000)
                    )

                    data_context = f"""
                    SEMESTERS:
                    {semesters.to_string(index=False)}

                    COURSES:
                    {courses.to_string(index=False)}

                    ACADEMIC CALENDAR:
                    {calendar.to_string(index=False)}

                    ASSESSMENTS:
                    {assessments.to_string(index=False)}

                    SCORES:
                    {scores.to_string(index=False)}
                    """

                    prompt = f"""
                    You are Degree AI, an assistant for an
                    engineering student.

                    Answer using ONLY the project data below.
                    Do not invent dates, marks, courses or rules.

                    If the answer is unavailable, reply exactly:
                    I cannot verify that from the current Degree OS data.

                    PROJECT DATA:
                    {data_context}

                    STUDENT QUESTION:
                    {question}
                    """

                    with st.spinner("Gemini is thinking..."):
                        interaction = client.interactions.create(
                            model="gemini-3.6-flash",
                            input=prompt,
                            background=True
                        )

                        while True:
                            interaction = client.interactions.get(
                                interaction.id
                            )

                            if interaction.status == "completed":
                                break

                            if interaction.status == "failed":
                               st.error("Gemini request failed.")
                               st.write("Error details:", interaction)
                               st.stop()

                            time.sleep(2)

                    st.subheader("AI Answer")
                    st.write(interaction.output_text)

                    st.caption("Source: Degree OS CSV files")

            except Exception as e:
                st.error("Unable to connect to Gemini.")
                st.write("Error:", str(e))

        else:
            st.warning("Please enter a question.")


# Data Admin page
elif page == "Data Admin":
    st.title("Data Admin")

    st.info("Manage and view your degree data files.")

    files = {
        "Semesters": semesters,
        "Courses": courses,
        "Academic Calendar": calendar,
        "Assessments": assessments,
        "Scores": scores
    }

    for name, df in files.items():
        with st.expander(name):
            if df.empty:
                st.warning("No data available.")
            else:
                st.write(f"Total rows: {len(df)}")
                st.dataframe(df, width="stretch")