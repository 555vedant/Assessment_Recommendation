# recommender/state.py
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

_df = None
_index = None
_model = None

def get_state():
    global _df, _index, _model

    if _df is None:
        print("Loading CSV...")
        _df = pd.read_csv("data/shl_catalog.csv").fillna("")

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    if _index is None:
        print("Loading FAISS index...")
        _index = faiss.read_index("recommender/index.faiss")

    return _df, _index, _model
