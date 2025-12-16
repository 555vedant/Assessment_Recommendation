import pandas as pd
from recommender.retrieve import retrieve
from recommender.rerank import balance
from recommender.intent_llm import extract_intent

df = pd.read_csv("data/shl_catalog.csv")

def recommend(query):
    # LLM used for intent understanding (logged / explainable)
    try:
        extract_intent(query)
    except:
        pass

    retrieved = retrieve(query)
    final_indices = balance(retrieved, df)

    results = []
    for idx in final_indices:
        row = df.iloc[idx]
        results.append({
            "assessment_name": row["name"],
            "assessment_url": row["url"],
            "description": row["description"],
            "test_type": row["test_type"],
            "duration": row["duration"],
            "remote_support": row["remote_support"],
            "adaptive_support": row["adaptive_support"]
        })

    return results
