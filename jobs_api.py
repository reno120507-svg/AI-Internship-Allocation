import requests
import pandas as pd


def get_live_internships():

    # Load Indian internships dataset
    indian_jobs = pd.read_csv("data/indian_internships.csv")

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

    api_jobs = []

    for job in data.get("data", []):

        api_jobs.append({
            "Company": job.get("employer_name", "Unknown"),
            "Role": job.get("job_title", "Intern"),
            "Location": job.get("job_city", "Remote"),
            "Apply Link": job.get("job_apply_link", "#")
        })

    api_df = pd.DataFrame(api_jobs)

    # Combine Indian dataset + API jobs
    jobs_df = pd.concat([indian_jobs, api_df], ignore_index=True)

    return jobs_df