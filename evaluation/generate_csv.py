import pandas as pd
from recommender.recommend import recommend

df = pd.read_csv("data/Gen_AI_Dataset.csv")
queries = df["query"].unique()

rows = []

for q in queries:
    recs = recommend(q)
    for r in recs:
        rows.append({
            "Query": q,
            "Assessment_url": r["assessment_url"]
        })

out = pd.DataFrame(rows)
out.to_csv("predictions.csv", index=False)

print(" predictions.csv generated")
