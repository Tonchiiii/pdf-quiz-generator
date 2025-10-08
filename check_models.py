# In check_models.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the library with your API key
try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    print("--- Successfully configured with API key. ---")
except Exception as e:
    print(f"--- FAILED to configure with API key. Error: {e} ---")
    exit()

print("\n--- Fetching available models... ---\n")

# List all available models
for model in genai.list_models():
    # We only care about models that support the 'generateContent' method
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model Name: {model.name}")
        print(f"  - Display Name: {model.display_name}")
        print(f"  - Supported Methods: {model.supported_generation_methods}\n")

print("--- End of list ---")