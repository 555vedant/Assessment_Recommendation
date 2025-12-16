import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    df = pd.read_csv("data/shl_catalog.csv")

    texts = (
        df["name"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["test_type"].fillna("")
    ).tolist()

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, show_progress_bar=True)

    with open("recommender/embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)

    print(" Embeddings saved")

if __name__ == "__main__":
    main()
