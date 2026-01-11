import pandas as pd
import datetime
import random
import re
import uvicorn
import requests
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Integration with your existing questions.py
try:
    from questions import get_explanation
except ImportError:
    def get_explanation(q_obj):
        return "Logic analysis module not found."

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize(text):
    if pd.isna(text): return ""
    return re.sub(r'[^\x20-\x7E]', '', str(text)).strip()

def load_daily_questions():
    try:
        apt_df = pd.read_csv('aptitudequestionbank.csv', quotechar='"', skipinitialspace=True)
        tech_df = pd.read_csv('technicalquestionbank.csv', quotechar='"', skipinitialspace=True)
        
        today_seed = int(datetime.date.today().strftime('%Y%m%d'))
        
        # Seeded sampling for daily consistency
        apt_samples = apt_df.sample(n=min(len(apt_df), 2), random_state=today_seed).to_dict('records')
        tech_samples = tech_df.sample(n=min(len(tech_df), 2), random_state=today_seed + 7).to_dict('records')
        
        pool = []
        for q in apt_samples + tech_samples:
            ans_key = str(q['answer']).strip().lower() 
            correct_text = sanitize(q[f"option_{ans_key}"])
            
            pool.append({
                "sq": q['sq'],
                "question": sanitize(q['question']),
                "options": [
                    sanitize(q['option_a']), 
                    sanitize(q['option_b']), 
                    sanitize(q['option_c']), 
                    sanitize(q['option_d'])
                ],
                "answer": correct_text,
                "type": q['type'],
                "category": q['category']
            })
        
        random.seed(today_seed)
        random.shuffle(pool)
        return pool
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.get("/get_questions")
async def get_questions():
    return load_daily_questions()

@app.get("/generate_logic")
async def generate_logic(question: str = Query(...), answer: str = Query(...)):
    mock_q_obj = {"question": question, "answer": answer}
    try:
        explanation = get_explanation(mock_q_obj)
        return {"explanation": explanation}
    except:
        return {"explanation": "Connection to logic engine failed."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)