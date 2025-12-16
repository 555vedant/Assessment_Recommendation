import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)
index = faiss.read_index("recommender/index.faiss")

def retrieve(query, k=50):
    q_emb = model.encode([query]).astype("float32")
    _, indices = index.search(q_emb, k)
    return indices[0]
