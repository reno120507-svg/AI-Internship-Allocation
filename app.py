import sqlite3
import streamlit as st
import pandas as pd
from matching import run_matching
from jobs_api import get_live_internships
from resume_parser import extract_resume_text, extract_skills
from skill_gap import analyze_skill_gap
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT,
role TEXT
)
""")

conn.commit()
cursor.execute(
"INSERT OR IGNORE INTO users VALUES ('admin','admin123','admin')"
)
conn.commit()
USER_DB = "data/users.csv"

st.set_page_config(page_title="AI Internship Allocation Engine", layout="centered")

st.write("NEW VERSION RUNNING")
st.title("🎓 AI-Based Smart Internship Allocation Engine")

st.markdown("""
This system intelligently matches **candidates** with **internship opportunities** using:

- Skill similarity
- Resume parsing
- Live internship listings
- Skill gap analysis
- Match score visualization
""")

# -----------------------------
# User Functions
# -----------------------------

def register_user(username, password):

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return False

    cursor.execute(
        "INSERT INTO users VALUES (?,?,?)",
        (username, password, "user")
    )

    conn.commit()
    return True


def login_user(username, password):

    cursor.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (username, password)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None


# -----------------------------
# Sidebar Login System
# -----------------------------

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if choice == "Login":

    if st.sidebar.button("Login"):

        role = login_user(username, password)

        if role:
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid username or password")


if choice == "Sign Up":

    if st.sidebar.button("Create Account"):

        if register_user(username, password):
            st.success("Account created successfully")
        else:
            st.error("Username already exists")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


# -----------------------------
# Main App (Only after login)
# -----------------------------

if st.session_state["logged_in"]:

    role = st.session_state.get("role", "user")

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.rerun()

    # -----------------------------
    # ADMIN DASHBOARD
    # -----------------------------

    if role == "admin":

        st.title("🛠 Admin Dashboard")

        admin_menu = st.sidebar.selectbox(
            "Admin Controls",
            ["View Users", "View Candidates", "View Internships"]
        )

        if admin_menu == "View Users":

            st.subheader("Registered Users")
            users_df = pd.read_csv("data/users.csv")
            st.dataframe(users_df)

        if admin_menu == "View Candidates":

            st.subheader("Candidates")
            candidates_df = pd.read_csv("data/candidates.csv")
            st.dataframe(candidates_df)

        if admin_menu == "View Internships":

            st.subheader("Internships")
            internships_df = pd.read_csv("data/internships.csv")
            st.dataframe(internships_df)

    # -----------------------------
    # NORMAL USER PAGE
    # -----------------------------

    else:

        st.title("AI Internship Matching System")

        # ---------------------------------------------
        # Candidate Profile
        # ---------------------------------------------

        st.subheader("👤 Candidate Profile")

        skills = st.text_input("Enter your skills (comma separated)")
        cgpa = st.number_input("Enter your CGPA", min_value=0.0, max_value=10.0)
        location_pref = st.text_input("Preferred Location")
        domain_pref = st.text_input("Preferred Domain (AI, Data, Web etc.)")

        # ---------------------------------------------
        # Resume Upload
        # ---------------------------------------------

        st.subheader("📄 Upload Resume")

        uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

        resume_skills = []

        if uploaded_resume:

            resume_text = extract_resume_text(uploaded_resume)
            resume_skills = extract_skills(resume_text)

            st.success("Skills detected from resume:")
            st.write(resume_skills)

        # ---------------------------------------------
        # Internship Matching
        # ---------------------------------------------

        st.subheader("🌍 Find Matching Internships")

        if st.button("Find Matching Internships"):

            jobs_df = get_live_internships()

            if resume_skills:
                user_skills = resume_skills
            else:
                user_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]

            matches = []

            for _, row in jobs_df.iterrows():

                role = str(row["Role"]).lower()
                location = str(row["Location"]).lower()

                job_text = (str(row["Role"]) + " " + str(row["Company"])).lower()

                skill_matches = sum(skill in job_text for skill in user_skills)
                skill_score = (skill_matches / max(len(user_skills), 1)) * 60

                domain_score = 0
                if domain_pref and domain_pref.lower() in role:
                    domain_score = 20

                location_score = 0
                if location_pref and location_pref.lower() in location:
                    location_score = 10

                cgpa_score = (cgpa / 10) * 10

                total_score = skill_score + domain_score + location_score + cgpa_score

                matches.append({
                    "Company": row["Company"],
                    "Role": row["Role"],
                    "Location": row["Location"],
                    "Match Score": round(total_score, 2),
                    "Apply Link": row["Apply Link"]
                })

            if matches:

                result_df = pd.DataFrame(matches)
                result_df = result_df.sort_values(by="Match Score", ascending=False)

                top_matches = result_df.head(5)

                best_match = top_matches.iloc[0]
                almost_matches = top_matches.iloc[1:]

                st.subheader("🏆 Best Internship Match")

                st.markdown(f"### {best_match['Role']} at {best_match['Company']}")
                st.write(f"📍 Location: {best_match['Location']}")
                st.write(f"⭐ Match Score: {best_match['Match Score']}")
                st.progress(int(best_match["Match Score"]))

                gap = analyze_skill_gap(user_skills, best_match["Role"])

                if gap["missing"]:

                    st.warning("Skill Gap Detected")
                    st.write("Recommended Skills To Learn:")

                    for skill in gap["missing"]:
                        st.write("•", skill)

                else:
                    st.success("You meet most required skills!")

                st.markdown(f"[Apply Here]({best_match['Apply Link']})")

                st.subheader("🤖 AI Recommended Internships (Top 5)")

                for _, row in almost_matches.iterrows():

                    st.markdown(f"**{row['Role']} — {row['Company']}**")
                    st.write(f"📍 Location: {row['Location']}")
                    st.write(f"⭐ Match Score: {row['Match Score']}")

                    gap = analyze_skill_gap(user_skills, row["Role"])

                    if gap["missing"]:

                        st.write("Recommended Skills To Learn:")

                        for skill in gap["missing"]:
                            if skill.isalpha():
                                st.write(f"• {skill}")

                    st.markdown(f"[Apply Here]({row['Apply Link']})")
                    st.markdown("---")

            else:
                st.warning("No matching internships found.")

        # ---------------------------------------------
        # AI Allocation Engine
        # ---------------------------------------------

        st.divider()

        st.subheader("📂 Run AI Allocation Engine")

        candidates_file = st.file_uploader("Upload Candidates CSV", type=["csv"])
        internships_file = st.file_uploader("Upload Internships CSV", type=["csv"])

        if st.button("🚀 Run Smart Allocation"):

            if candidates_file and internships_file:

                candidates_df = pd.read_csv(candidates_file)
                internships_df = pd.read_csv(internships_file)

                candidates_df.to_csv("data/candidates.csv", index=False)
                internships_df.to_csv("data/internships.csv", index=False)

                with st.spinner("Running AI Matching Engine..."):

                    final_df = run_matching()
                    final_df["Score"] = final_df["Score"].round(3)

                st.success("✅ Allocation Completed Successfully!")

                st.subheader("📊 Allocation Results")
                st.dataframe(final_df)

                st.download_button(
                    label="⬇ Download Allocation Results",
                    data=final_df.to_csv(index=False),
                    file_name="final_allocations.csv",
                    mime="text/csv"
                )

            else:
                st.warning("⚠ Please upload both CSV files.")

else:

    st.warning("Please login or create an account")