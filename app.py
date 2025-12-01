import streamlit as st
import datetime
from db import create_tables, get_questions_by_date, save_questions, save_user_answer
from questions import get_questions

# -------------------------
# Initialize DB
# -------------------------
create_tables()

st.title("2^two")
st.write("Solve 2 Aptitude + 2 Technical Questions Daily!")

# -------------------------
# Today's date
# -------------------------
today = datetime.date.today().isoformat()

# -------------------------
# Regenerate Questions Button (ADDED st.rerun())
# -------------------------
if st.button("Regenerate Questions"):
    new_questions = get_questions()
    save_questions(today, new_questions, overwrite=True)  # overwrite old ones
    st.session_state.questions_cached = new_questions
    st.session_state.q_index = 0
    st.session_state.answers = []
    st.session_state.submitted = False
    st.session_state.user_choice = None
    st.success("Questions regenerated and saved from updated prompt!")
    st.rerun() # <-- ADDED: Force immediate reload to show new question

# -------------------------
# Load questions (UPDATED LOGIC: Always generate if cache is empty)
# -------------------------
if 'questions_cached' not in st.session_state:
    # This logic forces a new generation and ignores the old check for saved questions
    # for the current day, addressing the "ignore daily logic" request.
    with st.spinner("Generating Fresh Questions..."):
        questions = get_questions()
        
        # Save new questions to the DB and session state, overwriting any old set
        save_questions(today, questions, overwrite=True)
        
        st.session_state.questions_cached = questions
        
        # Initialize state for a new quiz
        st.session_state.q_index = 0
        st.session_state.answers = []
        st.session_state.submitted = False
        st.session_state.user_choice = None
        
        st.success("Fresh Questions are Ready!")
else:
    # If the cache exists, load it (Standard Streamlit persistence)
    questions = st.session_state.questions_cached

total_questions = len(questions)

# -------------------------
# Session State (Unchanged)
# -------------------------
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'user_choice' not in st.session_state:
    st.session_state.user_choice = None

# -------------------------
# Quiz Complete (Unchanged)
# -------------------------
if st.session_state.q_index >= total_questions:
    st.balloons()
    st.success("🎉 Quiz Completed! 🎉")
    st.write(f"Your Score: {sum(ans['correct'] for ans in st.session_state.answers)}/{total_questions}")
    st.write("Summary:")
    for ans in st.session_state.answers:
        q = next(q for q in questions if q["id"] == ans["id"])
        st.write(f"**Q: {q['question']}**")
        st.write(f"Your answer: {ans['choice']} | Correct: {q['answer']}")
        st.write(f"💡 Explanation: {q['explanation']}")
    st.stop()

# -------------------------
# Current Question (Unchanged)
# -------------------------
current_q = questions[st.session_state.q_index]
st.write(f"**Q{st.session_state.q_index + 1}: {current_q['question']}**")

# -------------------------
# Single Progress Bar (Unchanged)
# -------------------------
answered_questions = st.session_state.q_index
if st.session_state.submitted:
    answered_questions += 1
st.progress(answered_questions / total_questions)

# -------------------------
# Display Options or Explanation
# -------------------------
if not st.session_state.submitted:
    # Show options
    user_choice_local = st.radio(
        "Choose an option:",
        [f"{key}: {val}" for key, val in current_q["options"].items()],
        key=f"radio_{st.session_state.q_index}"
    )

    if st.button("Submit Answer"):
        if not user_choice_local:
            st.warning("Please select an option before submitting!")
        else:
            choice_key = user_choice_local.split(":")[0]
            correct = current_q["answer"]
            is_correct = choice_key == correct

            # Save answer
            save_user_answer(current_q["id"], choice_key, is_correct)
            st.session_state.answers.append({
                "id": current_q["id"],
                "choice": choice_key,
                "correct": is_correct
            })

            st.session_state.user_choice = choice_key
            st.session_state.submitted = True
            st.rerun() # <-- ADDED: Fixes the double-click issue

else:
    # After submission, show explanation and Next button
    st.write("💡 Explanation:", current_q["explanation"])

    if st.button("Next Question"):
        st.session_state.q_index += 1
        st.session_state.submitted = False
        st.session_state.user_choice = None
        st.rerun() # <-- ADDED: Fixes the double-click issue