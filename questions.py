import os
import json
import random
from dotenv import load_dotenv
import uuid
import requests
from typing import List, Dict, Any

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("FATAL WARNING: OPENROUTER_API_KEY not found. Using fallback questions.")

# -------------------------
# API client info (OpenAI Compatible)
# -------------------------
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Recommended stable, free model known for strong JSON structured output
OPENROUTER_MODEL = "tngtech/deepseek-r1t2-chimera:free" 

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    # Required for OpenRouter security check (use http://localhost for development)
    "HTTP-Referer": "http://localhost" 
}

# -------------------------
# Prompt for MCQs (Final Topics and 30-Word Limit)
# -------------------------
PROMPT = """
Generate exactly 4 multiple-choice questions for CSE technical interview level:

- 2 aptitude questions: Focused on **Quantitative Ability and Logical Reasoning** from the following topics: Sequences & Series, Permutations & Combinations, Probability, Geometry, Mensuration, Statistics, Blood Relations, Directions, Clocks & Calendars, Cubes, Coding & Decoding, Cryptarithmetic, and Non Verbal Reasoning.
- 2 technical questions: Focused on **Core Computer Science** concepts such as Data Structures, Algorithms, Operating Systems, and Database Management Systems.

Requirements:

1. Each question must have exactly 4 options (A, B, C, D).
2. The correct answer must be randomly placed among the options; do not always put it at A.
3. Provide one correct answer only.
4. Provide a concise explanation for why the correct answer is correct, **maximum 30 words**.
5. Format the output strictly as a JSON list like this:

[
  {
    "type": "aptitude or technical",
    "question": "question text",
    "options": {
      "A": "option text",
      "B": "option text",
      "C": "option text",
      "D": "option text"
    },
    "answer": "A/B/C/D",
    "explanation": "short explanation (MAX 30 WORDS)"
  }
]

Do not include any text outside the JSON. Ensure that the options for each question are shuffled.
"""

# -------------------------
# Generate questions from OpenRouter
# -------------------------
def generate_questions():
    if not OPENROUTER_API_KEY:
        return None
    
    unique_prompt = PROMPT + f"\n\n--- Request Seed: {uuid.uuid4()} ---"

    payload = {
        "model": OPENROUTER_MODEL,
        "response_format": {"type": "json_object"}, # CRUCIAL for reliable JSON
        "messages": [
            {"role": "system", "content": "You are an expert quiz generator. Your response must be a valid JSON array, strictly adhering to the user's required structure."},
            {"role": "user", "content": unique_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000 
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status() 
        data = response.json()
        
        # OpenRouter/OpenAI parsing
        text = data['choices'][0]['message']['content']
        
        # 1. Clean markdown code block if present
        if text.strip().startswith("```json"):
            text = text.strip().strip("```json").strip("```")

        # 2. Find the start and end of the JSON array for robustness
        try:
            json_start = text.index('[')
            json_end = text.rindex(']')
            # Slice the text to include only the content from '[' to ']'
            text = text[json_start : json_end + 1]
        except ValueError:
            # If brackets are not found, the output is fundamentally broken
            print("Error: Could not find valid JSON array markers ([...]) in LLM output.")
            print("RAW OUTPUT:", text)
            return None

        # --- END OF NEW ROBUST CLEANUP LOGIC ---
        
        questions = json.loads(text)
        
        # Shuffle options (Existing logic)
        for q in questions:
            opts = list(q['options'].items())
            random.shuffle(opts)
            shuffled = {k: v for k, v in opts}
            correct_value = q['options'][q['answer']]
            for key, val in shuffled.items():
                if val == correct_value:
                    q['answer'] = key
                    break
            q['options'] = shuffled
            
        return questions
    
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', 'N/A')
        print(f"OpenRouter API Error: HTTP Status {status_code}. Reason: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing model output: JSON Decode Error. Check model response format. RAW OUTPUT: {text}")
        return None
    except Exception as e:
        print(f"Unexpected generation error: {e}")
        return None

# -------------------------
# Fallback sample questions (Used if API fails)
# -------------------------
def generate_sample_questions():
    return [
        {
            "type": "aptitude",
            "question": "What is 2 + 2?",
            "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
            "answer": "B",
            "explanation": "2 + 2 = 4 (Maximum 30 Words)."
        },
        {
            "type": "aptitude",
            "question": "If a train travels 60 km in 1 hour, how far will it travel in 2.5 hours?",
            "options": {"A": "120 km", "B": "150 km", "C": "180 km", "D": "200 km"},
            "answer": "B",
            "explanation": "Distance = Speed × Time. 60 km/h * 2.5 h = 150 km. (Maximum 30 Words)."
        },
        {
            "type": "technical",
            "question": "Which data structure uses LIFO?",
            "options": {"A": "Queue", "B": "Stack", "C": "List", "D": "Tree"},
            "answer": "B",
            "explanation": "Stack uses Last-In, First-Out (LIFO) order, meaning the last element added is the first one removed. (Maximum 30 Words)."
        },
        {
            "type": "technical",
            "question": "What is normalization in a database?",
            "options": {"A": "Organizing data to minimize redundancy", "B": "Optimizing search speed", "C": "Adding indexes to tables", "D": "Encrypting data for security"},
            "answer": "A",
            "explanation": "Normalization is the process of organizing the columns and tables in a database to reduce data redundancy and improve data integrity. (Maximum 30 Words)."
        }
    ]

# -------------------------
# Parse / normalize questions
# -------------------------
def parse_questions(raw_questions: List[Dict[str, Any]]):
    if not raw_questions:
        return []
    parsed = []
    for idx, q in enumerate(raw_questions):
        parsed.append({
            "id": idx + 1,
            "type": q.get("type", ""),
            "question": q.get("question", ""),
            "options": q.get("options", {}),
            "answer": q.get("answer", ""),
            "explanation": q.get("explanation", "")
        })
    return parsed

# -------------------------
# Convenience function for app
# -------------------------
def get_questions():
    raw = generate_questions()
    if not raw:
        print("Using fallback sample questions.")
        raw = generate_sample_questions()
    return parse_questions(raw)