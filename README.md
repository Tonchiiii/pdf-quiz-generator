
# 🧠 PDF Quiz Generator
An intelligent web application that automatically generates interactive quizzes from any PDF document. This tool allows users to upload a PDF, specify a page range, and instantly receive a custom quiz to test their knowledge.

(Tip: Take a screenshot of your app, upload it to a site like imgur.com, and paste the link here.)

---

## 🚀 Features

- **PDF Upload**: Upload any PDF file to use as a source for your quiz.

**Custom Page Range**: Focus your quiz on the exact content you need by selecting a specific start and end page.

**Variable Quiz Length**: Choose the number of questions you want (from 1 to 20).

**Interactive Quiz**: Take the quiz directly in the app with interactive radio buttons for your answers.

**Instant Scoring**: Submit your quiz to see your score, with correct answers highlighted and incorrect answers corrected.

**AI-Powered**: Uses a hybrid AI model approach (Google Gemini for generation, OpenAI for embeddings) for fast and accurate results.

---

## 💻 Tech Stack
- **Frontend:** Streamlit

- **AI Orchestration:** LangChain

### Core AI Models:

- **Generation:** Google Gemini (gemini-flash-latest)

- **Embeddings:** OpenAI Embeddings API

- **Backend & PDF Processing:** Python, pypdf, chromadb

---

## 🏃 How to Run This Project Locally
Interested in running the app on your own machine? Here’s how:

1. **Prerequisites**
- Python 3.9 or newer

- Git

- An API key from OpenAI (must have a payment method on file)

- An API key from Google AI Studio

2. **Clone the Repository**
   ````bash
   git clone https://github.com/Tonchiiii/pdf-quiz-generator.git
   cd pdf-quiz-generator

3. **Set Up a Virtual Environment**
It's a best practice to keep project dependencies isolated.

   ````bash
   python -m venv venv
   source venv/Scripts/activate


4. **Install Dependencies**
Install all the necessary Python libraries from requirements.txt.
 
   ````bash
   pip install -r requirements.txt

5. **Create Your Environment File**
This project requires API keys to function. Create a file named .env in the root of the project folder.

   ````bash
   touch .env

6. Now, open the .env file and add your secret keys. It should look like this:
   
   ````bash
   OPENAI_API_KEY="sk-YourOpenAIKeyHere"
   GOOGLE_API_KEY="AIzaSy-YourGoogleKeyHere"

7. **Run the App!**
You're all set. Use Streamlit to run the application.

   ````bash
   streamlit run app.py

Your browser should automatically open to **http://localhost:8501**, and you'll see the app running locally.

