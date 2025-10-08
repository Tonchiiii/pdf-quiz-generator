# In core_logic.py

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
#from langchain_openai import OpenAIEmbeddings, ChatOpenAI                                 # Uncomment if using OpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI   
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Load environment variables from .env file
load_dotenv()

def generate_quiz_from_pdf(pdf_path, number_of_questions):
    """
    This function takes a path to a PDF file and the number of questions,
    then generates a quiz.
    """
    try:
        # 1. Load the PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # 2. Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        # 3. Create embeddings and store in a vector database
        #embeddings = OpenAIEmbeddings()                                            # Uncomment if using OpenAI
        #embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")    # Uncomment if using Google Gemini
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = Chroma.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever()

        # 4. Define the prompt template
        template = """
        You are an expert quiz maker. Based on the context provided, generate {number} multiple-choice questions.
        The output should be a JSON array, where each element is an object with the following structure:
        {{
          "question": "The question text",
          "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
          "answer": "The full text of the correct option"
        }}
        Do not include any other text or explanations outside of the JSON array.

        Context:
        {context}
        """
        prompt = ChatPromptTemplate.from_template(template)


        # 5. Initialize the LLM
        #llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.4)               # Uncomment if using OpenAI    
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.4, convert_system_message_to_human=True) # Gemini Pro

        # 6. Create the RAG chain
        rag_chain = (
            {"context": retriever, "number": lambda x: number_of_questions}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 7. Invoke the chain to get the quiz
        quiz = rag_chain.invoke("")
        return quiz

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example of how to run this (for testing purposes)
if __name__ == '__main__':
    # Create a dummy PDF for testing if you don't have one
    # You can also just place a PDF in your project folder
    test_pdf_path = "sample.pdf" # Make sure this file exists
    num_questions = 5

    if os.path.exists(test_pdf_path):
        quiz_result = generate_quiz_from_pdf(test_pdf_path, num_questions)
        if quiz_result:
            print("--- Generated Quiz ---")
            print(quiz_result)
    else:
        print(f"Test PDF not found at: {test_pdf_path}")