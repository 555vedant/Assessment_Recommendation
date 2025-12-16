import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_intent(query: str) -> dict:
    prompt = f"""
    Extract skills from this hiring query.
    Return JSON with keys:
    hard_skills, soft_skills
    Query: {query}
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text
