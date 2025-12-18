# recommender/recommend.py
import json
import pandas as pd
import google.generativeai as genai
import os
import time
from recommender.retrieve import retrieve
from recommender.intent_llm import extract_intent
from recommender.state import get_state
from recommender.debug_utils import log_event, get_mem_info, write_file

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def recommend(query, useLLM):
    call_id = int(time.time() * 1000)
    log_event("RECOMMEND_START", f"id={call_id}, useLLM={useLLM}, query_len={len(query)}")
    start = time.time()

    # Lazy-load CSV and resources
    df, _, _ = get_state()
    log_event("RECOMMEND_MEM_AFTER_STATE", str(get_mem_info()))

    intent = {}
    if useLLM:
        try:
            intent = extract_intent(query)
            log_event("RECOMMEND", "intent extracted")
        except Exception as e:
            log_event("RECOMMEND", f"intent error: {e}")
            intent = {}

    # build augmented query
    if useLLM and intent:
        augmented_query = query + " " + " ".join(
            intent.get("hard_skills", []) + intent.get("soft_skills", [])
        )
    else:
        augmented_query = query

    log_event("RECOMMEND", f"using augmented_query length={len(augmented_query)}")
    log_event("RECOMMEND_MEM_BEFORE_RETRIEVE", str(get_mem_info()))
    candidate_indices = retrieve(augmented_query, k=30)
    log_event("RECOMMEND_MEM_AFTER_RETRIEVE", str(get_mem_info()))

    if not candidate_indices:
        log_event("RECOMMEND", "no candidate indices returned")
        return []

    candidates_df = df.iloc[candidate_indices].copy()

    # Duration constraint
    if "minute" in query.lower():
        try:
            durations = (
                candidates_df["duration"]
                .str.extract(r"(\d+)")
                .astype(float)[0]
                .fillna(999)
            )
            candidates_df = candidates_df[durations <= 45]
        except Exception as e:
            log_event("RECOMMEND", f"duration filter error: {e}")

    # Balance hard & soft
    hard = candidates_df[candidates_df["test_type"].str.contains("K", na=False)]
    soft = candidates_df[candidates_df["test_type"].str.contains("P|C", na=False)]
    final_df = pd.concat([hard.head(3), soft.head(2)]).head(5)
    log_event("RECOMMEND", f"final_df rows={len(final_df)}")
    log_event("RECOMMEND_MEM_BEFORE_RERANK", str(get_mem_info()))

    # Reranking using LLM (best-effort)
    if useLLM and not final_df.empty:
        try:
            # shrink the prompt: do NOT include long descriptions in prod debug
            llm_candidates = final_df[["name", "url", "test_type"]].to_dict("records")
            rerank_prompt = f"""
            You are selecting the most relevant SHL assessments.

            User query:
            {query}

            Assessments:
            {json.dumps(llm_candidates, indent=2)}

            Select the BEST 5 assessments.
            Return ONLY a JSON array of assessment URLs in ranked order.
            """
            log_event("RECOMMEND", "calling generative model for rerank")
            model = genai.GenerativeModel("gemini-flash-latest")
            response = model.generate_content(rerank_prompt)
            selected_urls = json.loads(response.text)
            final_df = final_df.set_index("url").loc[[u for u in selected_urls if u in final_df["url"].values]].reset_index()
            log_event("RECOMMEND", "LLM rerank success")
        except Exception as e:
            log_event("RECOMMEND", f"LLM rerank failed: {e}")
            # fallback; continue

    # Final response
    final_results = []
    for _, row in final_df.iterrows():
        duration = row["duration"]
        if not duration or str(duration).strip().upper() == "N/A":
            duration = "Variable"
        final_results.append({
            "assessment_name": row["name"],
            "assessment_url": row["url"],
            "description": row["description"],
            "test_type": row["test_type"],
            "duration": duration,
            "remote_support": row["remote_support"],
            "adaptive_support": row["adaptive_support"]
        })

    total = round(time.time() - start, 3)
    log_event("RECOMMEND_DONE", f"id={call_id}, total_s={total}, returned={len(final_results)}")
    log_event("RECOMMEND_MEM_END", str(get_mem_info()))
    return final_results
