import streamlit as st
import random
import json
import os
import re
import math
from datetime import datetime
import pandas as pd

# local imports (make sure these files exist)
from quiz_data import quiz_questions   # your question bank
from planner import create_study_plan  # your planner function

# ------------------ Page settings ------------------
st.set_page_config(page_title="Education Learning Agent", page_icon="📚", layout="wide")

# ------------------ Files used ------------------
USERS_FILE = "users.json"
SCORES_FILE = "scores.json"
DOUBTS_FILE = "doubts.csv"

# ------------------ Utility functions ------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return {}
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_scores(data):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_doubt(text):
    # append to CSV-like file (comma separated) safely
    line = text.replace("\n", " ").replace("\r", " ")
    with open(DOUBTS_FILE, "a", encoding="utf-8") as f:
        f.write(f'"{line}"\n')

# ------------------ Header ------------------
st.markdown("""
    <h1 style='text-align:center; color:#2b6cb0; margin-bottom:2px;'>📚 Education Learning Agent</h1>
    <p style='text-align:center; color:gray; margin-top:0; margin-bottom:16px;'>
        Practice quizzes, ask doubts and plan your study — simple and offline.
    </p>
""", unsafe_allow_html=True)

# ------------------ Top menu ------------------
menu = st.selectbox("Menu", ["Home", "Ask Doubt", "Take Quiz", "Study Planner", "Progress", "Motivation"])

# ensure session state keys
if "quiz_user" not in st.session_state:
    st.session_state.quiz_user = None

# small helper to display login status in header area
if st.session_state.quiz_user:
    st.markdown(f"<div style='text-align:right; color: #0f5132;'>Logged in as **{st.session_state.quiz_user}**</div>", unsafe_allow_html=True)

# ------------------ HOME ------------------
if menu == "Home":
    st.subheader("Welcome!")
    st.write("- Solve quick doubts (Math / Science / English).")
    st.write("- Take randomized quizzes (login required for quizzes).")
    st.write("- Create a study plan and view progress.")
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Quizzes taken", value="—")
    with c2:
        st.metric("Doubts asked", value="—")
    with c3:
        st.metric("Study hours today", value="—")

# ------------------ ASK DOUBT ------------------
elif menu == "Ask Doubt":
    st.header("Ask Any Doubt (Maths / English / Science)")
    user_q = st.text_input("Enter your question (example: What is square root of 144?)")

    if st.button("Submit Doubt"):
        if not user_q or user_q.strip() == "":
            st.warning("Please type a question.")
        else:
            q = user_q.strip()
            append_doubt(q)
            # attempt rule-based answer
            ans = None
            ql = q.lower()

            try:
                # --- Math ---
                if any(op in ql for op in ["+", "-", "*", "/", "calculate", "%", "percent"]) or "square root" in ql or "sqrt" in ql:
                    if "square root" in ql or "sqrt" in ql:
                        nums = re.findall(r'\d+\.?\d*', ql)
                        if nums:
                            n = float(nums[0])
                            ans = f"√{int(n)} = {math.sqrt(n):g}"
                    elif "percent" in ql or "%" in ql:
                        nums = re.findall(r'\d+\.?\d*', ql)
                        if len(nums) >= 2:
                            percent = float(nums[0]); value = float(nums[1])
                            ans = f"{percent}% of {value} = {(percent/100)*value:g}"
                    else:
                        # safe expression extraction
                        expr = re.sub(r'[^0-9+\-*/(). ]', '', ql)
                        if expr.strip():
                            try:
                                ans = f"Answer: {eval(expr)}"
                            except:
                                ans = None

                # --- Science facts ---
                if ans is None:
                    science_db = {
                        "photosynthesis": "Plants make food using sunlight, CO₂ and water (chlorophyll involved).",
                        "gravity": "A force that pulls objects toward the Earth (gives objects weight).",
                        "atom": "Smallest unit of an element containing protons, neutrons and electrons.",
                        "evaporation": "Liquid turning into vapor due to heat.",
                        "acid": "Substance that donates H⁺ ions (pH < 7).",
                        "base": "Substance that releases OH⁻ ions (pH > 7)."
                    }
                    for k, v in science_db.items():
                        if k in ql:
                            ans = f"{k.capitalize()}: {v}"
                            break

                # --- English small dictionary ---
                if ans is None and ("meaning" in ql or ql.startswith("define")):
                    word = re.sub(r'^(what is |meaning of |define )', '', ql).strip().rstrip('?')
                    small_dict = {"timorous":"showing fear or lacking confidence", "benevolent":"kind and generous", "prudent":"acting with care for the future"}
                    if word in small_dict:
                        ans = f"Meaning of {word}: {small_dict[word]}"

                # fallback
                if ans is None:
                    ans = "Thanks — your question was recorded. A detailed answer will be added soon."

            except Exception:
                ans = "Sorry, couldn't process automatically."

            st.success(ans)

# ------------------ TAKE QUIZ ------------------
elif menu == "Take Quiz":
    st.header("📝 Quiz Section")

    # LOGIN REQUIRED FOR QUIZ (only here)
    if not st.session_state.quiz_user:
        st.subheader("🔐 Login to Continue Quiz")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # LOGIN
        with tab1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Login", key="login_btn"):
                users = load_users()
                if u in users and users[u]["password"] == hash_password(p):
                    st.session_state.quiz_user = u
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        # SIGNUP
        with tab2:
            new_u = st.text_input("Create username", key="signup_u")
            new_p = st.text_input("Create password", type="password", key="signup_p")
            if st.button("Sign Up", key="signup_btn"):
                users = load_users()
                if not new_u or not new_p:
                    st.warning("Username and password cannot be empty.")
                elif new_u in users:
                    st.warning("Username already exists. Choose another.")
                else:
                    users[new_u] = {"password": hash_password(new_p)}
                    save_users(users)
                    st.success("Signup successful — please login.")

        st.stop()  # stop until login

    # user is logged in for quiz
    st.success(f"Welcome {st.session_state.quiz_user}! 🎉")

    # quiz UI
    subject = st.selectbox("Choose subject", list(quiz_questions.keys()), index=0)
    level = st.selectbox("Difficulty (optional)", ["any", "easy", "medium", "hard"])
    # filter pool by level if available
    pool = quiz_questions.get(subject, [])
    if level != "any":
        pool = [q for q in pool if q.get("level", "easy") == level]
    n = min(5, len(pool))
    if n == 0:
        st.warning("No questions available for this subject/level.")
    else:
        # initialize session state for quiz
        if "quiz_started" not in st.session_state:
            st.session_state.quiz_started = False
        if "quiz_questions" not in st.session_state:
            st.session_state.quiz_questions = []
        if "quiz_idx" not in st.session_state:
            st.session_state.quiz_idx = 0
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = []

        if st.button("Start New Quiz", key="start_quiz_btn"):
            st.session_state.quiz_started = True
            st.session_state.quiz_questions = random.sample(pool, n)
            st.session_state.quiz_idx = 0
            st.session_state.quiz_answers = [None] * n

        if st.session_state.quiz_started and st.session_state.quiz_questions:
            idx = st.session_state.quiz_idx
            q = st.session_state.quiz_questions[idx]
            st.markdown(f"**Q {idx+1}. {q['question']}**")

            # options with placeholder
            options = ["-- Select an answer --"] + q["options"]
            choice = st.radio("Select answer", options, key=f"quiz_radio_{idx}")
            if choice != "-- Select an answer --":
                st.session_state.quiz_answers[idx] = choice

            # navigation with unique keys
            prev_col, next_col, submit_col = st.columns([1,1,1])
            with prev_col:
                if st.button("Previous", key=f"quiz_prev_{idx}"):
                    if st.session_state.quiz_idx > 0:
                        st.session_state.quiz_idx -= 1
            with next_col:
                if st.button("Next", key=f"quiz_next_{idx}"):
                    if st.session_state.quiz_idx < len(st.session_state.quiz_questions) - 1:
                        st.session_state.quiz_idx += 1
            with submit_col:
                if st.button("Submit Quiz", key="quiz_submit_btn"):
                    # calculate score
                    score = 0
                    for ua, qq in zip(st.session_state.quiz_answers, st.session_state.quiz_questions):
                        if ua == qq.get("answer"):
                            score += 1
                    st.success(f"Your Score: {score} / {len(st.session_state.quiz_questions)}")

                    # save score to SCORES_FILE per user
                    scores = load_scores()
                    user = st.session_state.quiz_user or "guest"
                    if user not in scores:
                        scores[user] = []
                    scores[user].append({
                        "subject": subject,
                        "level": level,
                        "score": score,
                        "total": len(st.session_state.quiz_questions),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    save_scores(scores)
                    st.info("Score saved to your history.")

                    # reset quiz state
                    st.session_state.quiz_started = False
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_answers = []
                    st.session_state.quiz_idx = 0

# ------------------ STUDY PLANNER ------------------
elif menu == "Study Planner":
    st.header("📘 Study Planner")

    subject = st.selectbox("Choose subject", ["Math", "Science", "English"])
    hours = st.number_input("How many hours do you have today?", min_value=1, max_value=12, step=1)
    if st.button("Create Plan"):
        plan = create_study_plan(int(hours), subject=subject)
        st.write(f"### Your Study Plan for {subject}:")
        for p in plan:
            st.write("•", p)
        if plan:
            hours_list = [0.5, 0.5, 1, 1, 1][:len(plan)]
            df = pd.DataFrame({"Task": plan, "Hours": hours_list})
            st.write("Study Hours Distribution")
            st.bar_chart(df.set_index("Task"))

# ------------------ PROGRESS (Score History) ------------------
elif menu == "Progress":
    st.header("📈 Progress & Score History")
    user = st.session_state.quiz_user
    scores = load_scores()

    if not user:
        st.info("Login to the Quiz first to see your personal progress.")
    else:
        user_scores = scores.get(user, [])
        if not user_scores:
            st.info("No quiz attempts saved yet.")
        else:
            # show table
            df = pd.DataFrame(user_scores)
            st.subheader("Your quiz attempts")
            st.dataframe(df.sort_values("time", ascending=False))

            # line chart of scores over attempts
            st.subheader("Score over time")
            df_plot = df.reset_index().sort_values("time")
            df_plot["attempt"] = range(1, len(df_plot) + 1)
            st.line_chart(df_plot.set_index("attempt")["score"])

            # average per subject bar chart
            st.subheader("Average score by subject")
            grouped = df.groupby("subject")["score"].mean().round(2)
            st.bar_chart(grouped)

# ------------------ MOTIVATION ------------------
elif menu == "Motivation":
    st.header("🌟 Motivation")
    quotes = [
        "Believe you can and you're halfway there.",
        "Don’t stop until you’re proud.",
        "Small steps every day lead to big results.",
        "Hard work beats talent when talent doesn't work hard.",
        "Success is the sum of small efforts repeated daily."
    ]
    st.info(random.choice(quotes))
