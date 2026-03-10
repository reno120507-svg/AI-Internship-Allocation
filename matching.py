import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def run_matching():
    candidates = pd.read_csv("data/candidates.csv")
    internships = pd.read_csv("data/internships.csv")

    all_skills = list(candidates["skills"]) + list(internships["required_skills"])

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_skills)

    candidate_vectors = tfidf_matrix[:len(candidates)]
    internship_vectors = tfidf_matrix[len(candidates):]

    results = []

    for i, candidate in candidates.iterrows():
        for j, internship in internships.iterrows():

            skill_score = cosine_similarity(
                candidate_vectors[i],
                internship_vectors[j]
            )[0][0]

            cgpa_score = candidate["cgpa"] / 10 if candidate["cgpa"] >= internship["min_cgpa"] else 0
            location_score = 1 if candidate["location_pref"] == internship["location"] else 0
            domain_score = 1 if candidate["domain_pref"] == internship["domain"] else 0

            final_score = (
                0.5 * skill_score +
                0.2 * cgpa_score +
                0.2 * location_score +
                0.1 * domain_score
            )

            results.append({
                "Candidate": candidate["name"],
                "Company": internship["company"],
                "Score": final_score
            })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="Score", ascending=False)

    allocated_candidates = set()
    allocated_companies = set()
    final_allocations = []

    for _, row in result_df.iterrows():
        if row["Candidate"] not in allocated_candidates and row["Company"] not in allocated_companies:
            allocated_candidates.add(row["Candidate"])
            allocated_companies.add(row["Company"])
            final_allocations.append(row)

    final_df = pd.DataFrame(final_allocations)

    print("\nFINAL OPTIMAL ALLOCATIONS:\n")
    print(final_df)

    return final_df


if __name__ == "__main__":
    final_df = run_matching()
    final_df.to_csv("final_allocations.csv", index=False)