# recommender/retrieve.py
import numpy as np
from recommender.state import get_state

def retrieve(query, k=30):
    _, index, model = get_state()

    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")
    _, indices = index.search(q_emb, k)

    return indices[0].tolist()
