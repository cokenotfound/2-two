import os
import requests
from dotenv import load_dotenv

# Initialize dotenv to read from your local .env file
load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "tngtech/deepseek-r1t2-chimera:free" 

def get_explanation(q_data: dict) -> str:
    """
    Fetches explanation using the .env API key.
    """
    # OG Logic: Prioritize environment variables from .env
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # If not found in .env, check st.secrets (useful for live deployment)
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENROUTER_API_KEY")
        except:
            api_key = None

    if not api_key:
        return "Explanation unavailable: API Key not found in .env or secrets."

    prompt = f"""
    Explain this {q_data.get('category')} question.
    Topic: {q_data.get('type')}
    Question: {q_data.get('question')}
    Options: {q_data.get('options')}
    Correct Answer: {q_data.get('answer')}

    Requirement: Provide a 50-100 word logical explanation.
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a CSE tutor. Provide only the explanation."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        explanation = data['choices'][0]['message']['content'].strip()
        
        if "</thought>" in explanation:
            explanation = explanation.split("</thought>")[-1].strip()
            
        return explanation
    except Exception as e:
        return f"Error: {str(e)}"