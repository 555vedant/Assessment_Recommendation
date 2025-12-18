# api.py
import time
import traceback
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from recommender.recommend import recommend
from recommender.debug_utils import log_event, get_mem_info, write_file

# configure logging to stdout and file (Render collects stdout)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

class Query(BaseModel):
    query: str
    useLLM: bool = False  # optional flag from frontend

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/debug-logs")
def debug_logs(lines: int = 200):
    """
    Helper to fetch last N lines of log for quick debugging (temporary).
    """
    try:
        path = "/tmp/service.log"
        if not os.path.exists(path):
            return {"ok": False, "msg": "/tmp/service.log not found"}
        with open(path, "r") as f:
            data = f.read().splitlines()
        return {"ok": True, "last_lines": data[-lines:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/recommend")
def recommend_api(q: Query, request: Request):
    start = time.time()
    try:
        log_event("REQUEST", f"Incoming /recommend (useLLM={q.useLLM})")
        log_event("MEM_BEFORE", str(get_mem_info()))

        # call recommender - catch exceptions inside recommend too,
        # but we also guard here to capture crashes
        results = recommend(q.query, q.useLLM)

        log_event("MEM_AFTER", str(get_mem_info()))
        duration = round(time.time() - start, 3)
        log_event("REQUEST_DONE", f"Processed in {duration}s, returned {len(results)} items")
        return {"query": q.query, "recommendations": results}
    except Exception as exc:
        # full traceback to /tmp/error.log and /tmp/service.log
        tb = traceback.format_exc()
        write_file("/tmp/error.log", tb)
        log_event("EXCEPTION", tb.splitlines()[-1] if tb else str(exc))
        # Return more info temporarily (REMOVE this in prod)
        return {
            "error": "internal_server_error",
            "message": str(exc),
            "trace_last_line": tb.splitlines()[-1] if tb else None
        }
