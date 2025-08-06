import streamlit as st
from typing import Optional, Literal
from pydantic import BaseModel, Field
from models import ModelState, Question
from tools import question_setter
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_perplexity import ChatPerplexity
from langchain_groq import ChatGroq
import random
import os

HISTORY_FILE = "history.txt"

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="📝 Haryana CET Practice Test", layout="centered")
st.title("📝 Haryana CET Practice Test")

TOPIC_OPTIONS = [
    "hssc cet haryana gk static",
    "haryana history",
    "haryana geography",
    "haryana economy",
    "haryana culture",
    "indian polity",
    "indian history",
    "indian geography",
    "general science",
    "current affairs",
    "sports",
    "awards and honours",
    "important days",
    "books and authors"
]

MODEL_OPTIONS = [
    "google|gemini-2.5-pro",
    "google|gemini-2.5-flash",
    "perplexity|sonar",
    "groq|llama3-70b-8192",
    "groq|mixtral-8x7b-32768",
    "groq|gemma-7b-it"
]

# --------------------------
# Top Selectors
# --------------------------
with st.container():
    col1, col2 = st.columns([4, 2])
    with col1:
        topic_selected = st.selectbox("Select Topic", options=TOPIC_OPTIONS, index=0, key="topic_selector")
    with col2:
        model_selected = st.selectbox("Select Model", options=MODEL_OPTIONS, index=0, key="model_selector")

# --------------------------
# Detailed Explanation Generator
# --------------------------
def explain_answer(question: Question):
    provider, model_name = st.session_state.get("model_selector").split("|")
    
    if provider == "google":
        model = GoogleGenerativeAI(temperature=0.3, model=model_name)
    elif provider == "perplexity":
        model = ChatPerplexity(temperature=0.3, model=model_name)
    elif provider == "groq":
        model = ChatGroq(temperature=0.3, model=model_name)
    else:
        raise ValueError("Unsupported model provider")

    prompt = PromptTemplate(
        template="""You are a teacher. Given the question:\n\n{question}\n\nExplain why the correct answer is:\n\n{answer}\n\nUse detailed but clear reasoning with facts and examples.""",
        input_variables=["question", "answer"]
    )
    
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"question": question.question, "answer": question.answer})

# --------------------------
# History View
# --------------------------
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
    st.stop()

st.markdown("### 10 Questions | Select the correct answer")

# --------------------------
# Load Questions
# --------------------------
def get_new_questions():
    state = ModelState(
        topic=st.session_state.get("topic_selector"),
        model=st.session_state.get("model_selector")
    )
    return question_setter(state).questions

# --------------------------
# Session State
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
# Start Test
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
        col1, col2, col3 = st.columns([3, 3, 3])
        with col3:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.8em; color: gray;'>[Source: {q.source}]</div>",
                unsafe_allow_html=True
            )
        st.markdown("---")

    if st.button("✅ Submit"):
        correct = 0
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=== New Test Attempt ===\nModel: {st.session_state.model_selector}\nTopic: {st.session_state.topic_selector}\n\n")
            for i, q in enumerate(st.session_state.current_questions):
                selected = st.session_state.selected_answers.get(i)
                if selected == q.answer:
                    correct += 1
                f.write(f"Q{i+1}. {q.question}\n")
                f.write(f"Correct answer: {q.answer}\n")
                f.write(f"Explanation: {q.explanation or 'N/A'}\n\n")

        st.session_state.score = correct
        st.session_state.submitted = True
        st.rerun()

# --------------------------
# Show Results + Explanation
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

        # Show built-in explanation
        if q.explanation:
            st.info(f"📘 Explanation: {q.explanation}")

        # Detailed explanation button + source
        col1, col2, col3 = st.columns([3, 3, 3])
        with col1:
            if st.button(f"🧠 Detailed Explanation Q{i+1}", key=f"explain_btn_{i}"):
                st.session_state[f"show_explanation_q{i}"] = True
        with col3:
            st.markdown(
                f"<div style='text-align: right; font-size: 0.8em; color: gray;'>[Source: {q.source}]</div>",
                unsafe_allow_html=True
            )

        # Show detailed explanation if requested
        if st.session_state.get(f"show_explanation_q{i}", False):
            with st.spinner("Generating detailed explanation..."):
                detailed = explain_answer(q)
                st.success(f"🧠 Detailed Explanation: {detailed}")

        st.markdown("---")

    if st.button("🔁 Retake Test"):
        st.session_state.started = True
        st.session_state.submitted = False
        st.session_state.score = 0
        st.session_state.selected_answers = {}
        st.session_state.current_questions = random.sample(get_new_questions(), 10)
        st.rerun()
