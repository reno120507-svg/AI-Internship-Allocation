import requests
import pandas as pd


def get_live_internships():

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": "software intern OR ai intern OR machine learning intern OR data intern",
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": "190988e1eemsh01797a49b4a47a1p1b62d6jsnd611cc229b54",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    jobs = []

    for job in data["data"]:
        jobs.append({
            "Company": job.get("employer_name", "Unknown"),
            "Role": job.get("job_title", "Intern"),
            "Location": job.get("job_city", "Remote"),
            "Apply Link": job.get("job_apply_link", "#")
        })

    jobs_df = pd.DataFrame(jobs)

    return jobs_df