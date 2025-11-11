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
# This is crucial for remembering data across user interactions
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# --- Main App UI ---
st.title("🧠 PDF Quiz Generator")

# --- Sidebar for Settings ---
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    num_questions = st.number_input(
        "Number of questions", 
        min_value=1, 
        max_value=20, 
        value=5
    )
    
    # --- UPDATED PAGE RANGE INPUTS ---
    st.write("Filter pages (optional):")
    
    col1, col2 = st.columns(2)
    with col1:
        start_page_input = st.number_input(
            "Start page",
            min_value=1,
            value=None,
            placeholder="First",
            step=1
        )
    with col2:
        end_page_input = st.number_input(
            "End page",
            min_value=1,
            value=None,
            placeholder="Last",
            step=1
        )
    # -----------------------------------
    
    if st.button("Generate Quiz"):
        if uploaded_file is not None:
            # --- Validation for page range ---
            if start_page_input and end_page_input and start_page_input > end_page_input:
                st.error("Error: 'Start page' must be less than or equal to 'End page'.")
                st.stop() # Stop execution
            # -----------------------------------

            # Create a temporary directory if it doesn't exist
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Save the uploaded file to a temporary path
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Generating your quiz... This may take a moment."):
                try:
                    # Call the core logic function with new page arguments
                    quiz_text = generate_quiz_from_pdf(
                        temp_file_path, 
                        num_questions, 
                        start_page=start_page_input,
                        end_page=end_page_input
                    )
                    
                    # Handle potential errors from core_logic
                    if quiz_text.startswith("Error:"):
                        st.error(quiz_text)
                        st.session_state.quiz_data = None
                        st.stop()

                    # Clean the AI's output (in case it adds ```json ... ```)
                    if quiz_text.startswith("```json"):
                        quiz_text = quiz_text[7:-4].strip()
                    
                    # Parse the JSON
                    st.session_state.quiz_data = json.loads(quiz_text)
                    st.session_state.user_answers = {} # Reset answers
                    st.session_state.submitted = False # Reset submission state
                    st.success("Quiz generated! You can now take the quiz.")

                except json.JSONDecodeError:
                    st.error("Failed to parse the quiz. The AI may have returned an invalid format. Please try again.")
                    st.session_state.quiz_data = None
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state.quiz_data = None
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
        else:
            st.warning("Please upload a PDF file first.")

# --- Quiz Display and Interaction ---
if st.session_state.quiz_data:
    st.header("Take the Quiz!")
    
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"Question {i+1}: {q['question']}")
            
            # Use index=None to ensure no default answer is selected
            user_answers[i] = st.radio(
                "Choose your answer:", 
                q['options'], 
                key=f"q{i}", 
                index=None
            )

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
        user_answer = st.session_state.user_answers.get(i) # Use .get() for safety
        
        st.subheader(f"Question {i+1}: {q['question']}")
        
        if user_answer is None:
            st.warning("You did not answer this question.")
        elif user_answer == correct_answer:
            st.success(f"Your answer: **{user_answer}** (Correct!)")
            score += 1
        else:
            st.error(f"Your answer: **{user_answer}** (Incorrect)")
            st.info(f"Correct answer: **{correct_answer}**")
        st.markdown("---")
        
    st.balloons()
    st.title(f"Your final score: {score}/{len(st.session_state.quiz_data)}")

else:
    # Show a message on the main page if no file is uploaded yet
    if uploaded_file is None:
        st.info("Upload a PDF and click 'Generate Quiz' in the sidebar to begin.")