import pickle
import faiss
import numpy as np

def main():
    with open("recommender/embeddings.pkl", "rb") as f:
        embeddings = pickle.load(f)

    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "recommender/index.faiss")
    print("FAISS index created")

if __name__ == "__main__":
    main()
