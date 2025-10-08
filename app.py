# In app.py

import os
import streamlit as st
import json
from core_logic import generate_quiz_from_pdf

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF Quiz Generator",
    page_icon="🧠",
    layout="centered"
)

# --- Session State Initialization ---
# This is crucial for remembering the quiz data and user's answers
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# --- Main App UI ---
st.title("🧠 PDF Quiz Generator")

# Use a sidebar for the file uploader and settings
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
    
    if st.button("Generate Quiz"):
        if uploaded_file is not None:
            # Save temp file
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Generating your quiz..."):
                try:
                    quiz_text = generate_quiz_from_pdf(temp_file_path, num_questions)
                    # The AI might return a string enclosed in ```json ... ```, so we clean it
                    if quiz_text.startswith("```json"):
                        quiz_text = quiz_text[7:-4]
                    
                    st.session_state.quiz_data = json.loads(quiz_text)
                    st.session_state.user_answers = {} # Reset answers
                    st.session_state.submitted = False # Reset submission state
                except json.JSONDecodeError:
                    st.error("Failed to parse the quiz. The AI may have returned an invalid format. Please try again.")
                    st.session_state.quiz_data = None
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.quiz_data = None
                finally:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
        else:
            st.warning("Please upload a PDF file first.")

# --- Quiz Display and Interaction ---
if st.session_state.quiz_data:
    st.header("Take the Quiz!")
    
    # Create a form to group the radio buttons and the submit button
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"Question {i+1}: {q['question']}")
            # The key for each radio button must be unique
            
            # --- This is the line to change ---
            user_answers[i] = st.radio("Choose your answer:", q['options'], key=f"q{i}")

        # The submit button for the form
        submitted = st.form_submit_button("Submit Answers")

    if submitted:
        st.session_state.user_answers = user_answers
        st.session_state.submitted = True

# --- Results Display ---
if st.session_state.submitted:
    st.header("Quiz Results")
    score = 0
    for i, q in enumerate(st.session_state.quiz_data):
        correct_answer = q['answer']
        user_answer = st.session_state.user_answers[i]
        
        st.subheader(f"Question {i+1}: {q['question']}")
        
        if user_answer == correct_answer:
            st.success(f"Your answer: **{user_answer}** (Correct!)")
            score += 1
        else:
            st.error(f"Your answer: **{user_answer}** (Incorrect)")
            st.info(f"Correct answer: **{correct_answer}**")
        st.markdown("---")
        
    st.balloons()
    st.title(f"Your final score: {score}/{len(st.session_state.quiz_data)}")

else:
    if uploaded_file is None:
        st.info("Upload a PDF and click 'Generate Quiz' to begin.")