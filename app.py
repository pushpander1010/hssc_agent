import streamlit as st
from typing import Optional, Literal
from pydantic import BaseModel, Field
from models import ModelState
from tools import question_setter
import random
import os

HISTORY_FILE = "history.txt"

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(page_title="📝 Haryana CET Practice Test", layout="centered")
st.title("📝 Haryana CET Practice Test")

# ----- Topic & Model Options -----
TOPIC_OPTIONS = [
    "hssc cet haryana gk static",
    "hssc cet haryana history",
    "hssc cet haryana geography",
    "hssc cet haryana economy",
    "hssc cet haryana culture",
    "hssc cet indian polity",
    "hssc cet indian history",
    "hssc cet indian geography",
    "hssc cet general science",
    "hssc cet current affairs",
    "hssc cet sports",
    "hssc cet awards and honours",
    "hssc cet important days",
    "hssc cet books and authors",
    "hssc cet hindi",
    "hssc cet aptitude",
    "hssc cet reasoning",
    "hssc cet english",
    "hssc cet computers",
    "hssc cet JE mechanical",
    "hssc cet JE civil",
    "hssc cet environmental studies",
    "hssc cet traffic rules",
    "hssc cet rural haryana",
]

MODEL_OPTIONS = [
    "google|gemini-2.5-pro",
    "google|gemini-2.5-flash",
    "perplexity|sonar",
    "groq|llama3-70b-8192",
    "groq|mixtral-8x7b-32768",
    "groq|gemma-7b-it"
]

# ----- Top-right Dropdowns -----
with st.container():
    col1, col2 = st.columns([4, 2])
    with col1:
        topic_selected = st.selectbox(
            "Select Topic",
            options=TOPIC_OPTIONS,
            index=0,
            key="topic_selector"
        )
    with col2:
        model_selected = st.selectbox(
            "Select Model",
            options=MODEL_OPTIONS,
            index=0,
            key="model_selector"
        )

# ----- History Mode Toggle -----
if 'view_history' not in st.session_state:
    st.session_state.view_history = False

if st.button("📜 Revise Previous Questions"):
    st.session_state.view_history = True

if st.session_state.view_history:
    st.subheader("📖 History of Attempted Questions")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = f.read()
        st.text_area("📚 History", value=history, height=400)
    else:
        st.info("No history found yet.")

    if st.button("🔙 Back to Test"):
        st.session_state.view_history = False
        st.rerun()
    st.stop()  # Stop here to avoid rendering quiz

st.markdown("### 10 Questions | Select the correct answer")

# --------------------------
# Function to Load New Questions
# --------------------------
def get_new_questions():
    init_state = ModelState(
        topic=st.session_state.get("topic_selector"),
        model=st.session_state.get("model_selector")
    )
    return question_setter(init_state).questions

# --------------------------
# Session State Initialization
# --------------------------
if 'started' not in st.session_state:
    st.session_state.started = False
if 'selected_answers' not in st.session_state:
    st.session_state.selected_answers = {}
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_questions' not in st.session_state:
    st.session_state.current_questions = []

# --------------------------
# Start Test Button
# --------------------------
if not st.session_state.started:
    if st.button("🚀 Start Test"):
        st.session_state.started = True
        st.session_state.submitted = False
        st.session_state.score = 0
        st.session_state.selected_answers = {}
        st.session_state.current_questions = random.sample(get_new_questions(), 10)
        st.rerun()

# --------------------------
# Display Questions
# --------------------------
if st.session_state.started and not st.session_state.submitted:
    for i, q in enumerate(st.session_state.current_questions):
        st.markdown(f"**Q{i+1}. {q.question}**")
        st.session_state.selected_answers[i] = st.radio(
            label="Choose your answer:",
            options=q.options,
            key=f"q_{i}"
        )
        # Bottom-right source info
        col1, col2, col3 = st.columns([6, 1, 3])
        with col3:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.8em; color: gray;'>[Source: {q.source}]</div>",
                unsafe_allow_html=True
            )
        st.markdown("---")

    # Submit button
    if st.button("✅ Submit"):
        correct = 0
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=== New Test Attempt ===\n")
            f.write(f"Model: {st.session_state.model_selector}\n")
            f.write(f"Topic: {st.session_state.topic_selector}\n\n")
            for i, q in enumerate(st.session_state.current_questions):
                selected = st.session_state.selected_answers.get(i)
                if selected == q.answer:
                    correct += 1
                f.write(f"Q{i+1}. {q.question}\n")
                f.write(f"Your answer: {selected}\n")
                f.write(f"Correct answer: {q.answer}\n")
                f.write(f"Source: {q.source}\n\n")
            f.write(f"Score: {correct}/10\n\n")

        st.session_state.score = correct
        st.session_state.submitted = True
        st.rerun()

# --------------------------
# Show Results
# --------------------------
if st.session_state.submitted:
    st.success(f"🎉 You scored {st.session_state.score} out of 10")
    st.markdown("---")

    for i, q in enumerate(st.session_state.current_questions):
        user_ans = st.session_state.selected_answers.get(i)
        is_correct = user_ans == q.answer
        st.markdown(f"**Q{i+1}. {q.question}**")
        st.markdown(f"- Your answer: `{user_ans}`")
        st.markdown(f"- Correct answer: ✅ `{q.answer}`")
        st.markdown(f"{'✔️ Correct' if is_correct else '❌ Incorrect'}")

        # Source at bottom-right again
        col1, col2, col3 = st.columns([6, 1, 3])
        with col3:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.8em; color: gray;'>[Source: {q.source}]</div>",
                unsafe_allow_html=True
            )
        st.markdown("---")

    # Retake button
    if st.button("🔁 Retake Test"):
        st.session_state.started = True
        st.session_state.submitted = False
        st.session_state.score = 0
        st.session_state.selected_answers = {}
        st.session_state.current_questions = random.sample(get_new_questions(), 10)
        st.rerun()
