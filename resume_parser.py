import pdfplumber

def extract_resume_text(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:

        for page in pdf.pages:
            text += page.extract_text()

    return text.lower()


def extract_skills(resume_text):

    skill_keywords = [
        "python","java","c++","machine learning","deep learning",
        "data science","sql","excel","power bi","tableau",
        "javascript","react","node","html","css",
        "tensorflow","pytorch","nlp","ai","cloud","aws"
    ]

    found_skills = []

    for skill in skill_keywords:

        if skill in resume_text:
            found_skills.append(skill)

    return found_skills