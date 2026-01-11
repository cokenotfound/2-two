import streamlit as st
import pandas as pd
import datetime
import random
from questions import get_explanation

# --- PAGE CONFIG ---
st.set_page_config(page_title="2^Two Quiz", page_icon="📝")

# --- DATA LOADING LOGIC (2-CSV SELECTION) ---
@st.cache_data
def load_daily_questions():
    """
    Loads 2 questions from aptitudequestionbank.csv and 2 from technicalquestionbank.csv.
    Uses date-based seeds to ensure every user sees the same 4 questions daily.
    """
    try:
        # 1. Load CSV files (9-column format as discussed)
        apt_df = pd.read_csv('aptitudequestionbank.csv', quotechar='"', skipinitialspace=True)
        tech_df = pd.read_csv('technicalquestionbank.csv', quotechar='"', skipinitialspace=True)
        
        # 2. Create deterministic seed from today's date (YYYYMMDD)
        today_seed = int(datetime.date.today().strftime('%Y%m%d'))
        
        # 3. Pick 2 Aptitude Questions
        random.seed(today_seed)
        apt_samples = apt_df.sample(n=min(len(apt_df), 2)).to_dict('records')
        
        # 4. Pick 2 Technical Questions (using offset seed for independent randomness)
        random.seed(today_seed + 7) 
        tech_samples = tech_df.sample(n=min(len(tech_df), 2)).to_dict('records')
        
        # 5. Standardize into a single pool for the session state
        pool = []
        for q in apt_samples + tech_samples:
            pool.append({
                "sq": q['sq'],
                "question": q['question'],
                "options": {
                    "A": q['option_a'], "B": q['option_b'], 
                    "C": q['option_c'], "D": q['option_d']
                },
                "answer": str(q['answer']).strip().upper(),
                "type": q['type'],
                "category": q['category']
            })
        return pool
    except Exception as e:
        st.error(f"Error loading CSV files. Ensure filenames and headers are correct: {e}")
        return []

# --- APP INITIALIZATION ---
st.markdown("<h1>2<sup>Two</sup></h1>", unsafe_allow_html=True)
st.write("### Solve 2 Aptitude + 2 Technical Questions Daily!")

# Initialize Session State (OG Button/Flow Logic)
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = load_daily_questions()
    st.session_state.q_index = 0
    st.session_state.submitted = False
    st.session_state.current_explanation = ""

# --- QUIZ INTERFACE ---
if st.session_state.q_index < len(st.session_state.quiz_data):
    current_q = st.session_state.quiz_data[st.session_state.q_index]
    
    # Header & Progress Bar
    st.progress((st.session_state.q_index) / len(st.session_state.quiz_data))
    st.markdown(f"**Category:** {current_q['category']} | **Topic:** {current_q['type']}")
    st.write(f"#### Q{st.session_state.q_index + 1}: {current_q['question']}")
    
    # Selection (Standard OG Radio Logic)
    opts = [f"{k}: {v}" for k, v in current_q['options'].items()]
    user_choice = st.radio(
        "Select the correct answer:", 
        opts, 
        key=f"q_{current_q['sq']}_{st.session_state.q_index}"
    )
    
    # Action Buttons
    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            st.session_state.submitted = True
            st.rerun()
    else:
        # Correctness Check
        correct_key = current_q['answer']
        user_key = user_choice.split(":")[0]
        
        if user_key == correct_key:
            st.success(f"✨ Correct! The answer is indeed ({correct_key}).")
        else:
            st.error(f"❌ Incorrect. The correct answer was ({correct_key}).")
            
        # Get Real-time AI Explanation
        if not st.session_state.current_explanation:
            with st.spinner("AI is analyzing the solution..."):
                st.session_state.current_explanation = get_explanation(current_q)
        
        st.info(f"**Expert Explanation:**\n\n{st.session_state.current_explanation}")
        
        # Navigation to Next Question
        if st.button("Next Question"):
            st.session_state.q_index += 1
            st.session_state.submitted = False
            st.session_state.current_explanation = ""
            st.rerun()
else:
    # Final Screen
    st.balloons()
    st.success("🎉 Today's quiz is complete! Check back tomorrow for fresh questions.")
    if st.button("Restart Quiz (Practice Mode)"):
        # Reset state but maintain seeded selection until cache expires or date changes
        st.session_state.q_index = 0
        st.session_state.submitted = False
        st.session_state.current_explanation = ""
        st.rerun()