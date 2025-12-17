import pandas as pd
from evaluation.url_normalizer import normalize_to_solution_url

def extract_assessment_id(url):
    url = normalize_to_solution_url(url)
    return url.split("product-catalog/view/")[-1].strip("/").lower()


def recall_at_k(true_urls, pred_urls, k=10):
    true_ids = set(extract_assessment_id(u) for u in true_urls)
    pred_ids = [extract_assessment_id(u) for u in pred_urls[:k]]

    if not true_ids:
        return 0.0

    return len(true_ids.intersection(pred_ids)) / len(true_ids)


true_df = pd.read_csv("data/Gen_AI_Dataset.csv")
pred_df = pd.read_csv("predictions.csv")

recalls = []

for q in true_df["Query"].unique():
    gt = true_df[true_df["Query"] == q]["Assessment_url"].tolist()
    pr = pred_df[pred_df["Query"] == q]["Assessment_url"].tolist()
    recalls.append(recall_at_k(gt, pr, k=10))

print("Mean Recall@10:", sum(recalls) / len(recalls))
