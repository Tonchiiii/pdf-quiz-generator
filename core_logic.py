import os
from dotenv import load_dotenv

# Imports for the RAG pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings # The corrected import
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import Chroma

# Load environment variables from .env file
load_dotenv()

def generate_quiz_from_pdf(pdf_path, number_of_questions, start_page=None, end_page=None):
    """
    This function takes a path to a PDF file, the number of questions,
    and an optional page range, then generates a quiz in JSON format.
    """
    try:
        # 1. Load the PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # 2. Filter documents by page range if provided
        if start_page or end_page:
            # The 'page' metadata is zero-indexed (e.g., Page 1 is 0)
            
            # Determine start index
            # If user enters 1, start_index = 0
            start_index = (start_page - 1) if start_page else 0
            
            # Determine end index
            # If user enters 5, end_index = 5. We filter for page < 5 (i.e., 0,1,2,3,4)
            end_index = end_page if end_page else len(documents)

            # Ensure indices are valid
            start_index = max(0, start_index)
            end_index = min(len(documents), end_index)

            filtered_documents = [
                doc for doc in documents 
                if start_index <= doc.metadata['page'] < end_index
            ]
            
            # If the filter results in no documents, return an error
            if not filtered_documents:
                return "Error: No pages found within the specified page range. Please check the page numbers."
            
            documents = filtered_documents # Overwrite with the filtered list

        # 3. Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        # 4. Create embeddings and store in a vector database
        # We use a local, open-source embedding model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = Chroma.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever()

        # 5. Define the prompt template for JSON output
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

        # 6. Initialize the LLM (using the model you found works for your key)
        llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0.4, convert_system_message_to_human=True)

        # 7. Create the RAG chain
        rag_chain = (
            {"context": retriever, "number": lambda x: number_of_questions}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 8. Invoke the chain to get the quiz
        quiz = rag_chain.invoke("")
        return quiz

    except Exception as e:
        print(f"An error occurred in core_logic: {e}")
        return f"Error: {e}"
