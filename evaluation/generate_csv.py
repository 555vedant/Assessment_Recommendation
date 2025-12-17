import pandas as pd
from recommender.recommend import recommend
from evaluation.url_normalizer import normalize_to_solution_url

df = pd.read_csv("data/Gen_AI_Dataset.csv")

rows = []

for query in df["Query"].unique():
    results = recommend(query, useLLM=False) \

    for r in results:
        rows.append({
            "Query": query,
            "Assessment_url": normalize_to_solution_url(r["assessment_url"])
        })

pred_df = pd.DataFrame(rows)
pred_df.to_csv("predictions.csv", index=False)

print("predictions.csv generated with normalized URLs")
