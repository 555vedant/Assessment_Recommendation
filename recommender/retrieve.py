# recommender/retrieve.py
import time
from recommender.state import get_state
from recommender.debug_utils import log_event, get_mem_info

def retrieve(query, k=30):
    log_event("RETRIEVE", f"retrieve called; k={k}")
    t0 = time.time()
    df, index, model = get_state()  # lazy-load once
    log_event("RETRIEVE_MEM_POST_LOAD", str(get_mem_info()))

    # compute embedding and search
    try:
        # encode (use convert_to_numpy if available for less overhead)
        emb = model.encode([query], convert_to_numpy=True).astype("float32")
    except TypeError:
        # older sentence-transformers versions may not have convert_to_numpy
        emb = model.encode([query]).astype("float32")

    log_event("RETRIEVE_MEM_POST_EMBED", str(get_mem_info()))
    _, indices = index.search(emb, k)
    duration = round(time.time() - t0, 3)
    log_event("RETRIEVE_DONE", f"search took {duration}s")
    # return python list
    try:
        return indices[0].tolist()
    except Exception:
        # fallback
        return list(indices[0])
