TECH_SKILLS = [
    "python","java","c++","machine learning","deep learning",
    "data science","sql","excel","power bi","tableau",
    "javascript","react","node","html","css",
    "tensorflow","pytorch","nlp","ai","cloud","aws",
    "pandas","numpy","scikit-learn","docker","git","linux"
]

def analyze_skill_gap(user_skills, job_text):

    user_skills = [skill.lower() for skill in user_skills]

    matched = []
    missing = []

    job_text = job_text.lower()

    for skill in TECH_SKILLS:

        if skill in job_text:

            if skill in user_skills:
                matched.append(skill)

            else:
                missing.append(skill)

    return {
        "matched": matched,
        "missing": missing
    }