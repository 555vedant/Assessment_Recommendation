from fastapi import FastAPI
from pydantic import BaseModel
from threading import Thread
import time

from recommender.recommend import recommend
from recommender.state import get_state
from recommender.debug_utils import log_event

app = FastAPI()

class Query(BaseModel):
    query: str
    useLLM: bool = False


def background_preload():
    try:
        log_event("STARTUP", "Background preload started")
        get_state()
        log_event("STARTUP", "Background preload finished")
    except Exception as e:
        log_event("STARTUP_ERROR", str(e))


@app.on_event("startup")
def startup_event():
    Thread(target=background_preload, daemon=True).start()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend")
def recommend_api(q: Query):
    results = recommend(q.query, q.useLLM)
    return {
        "query": q.query,
        "recommendations": results
    }
