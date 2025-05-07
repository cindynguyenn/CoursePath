from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(".env loaded successfully!")
    print(f"Loaded API Key starts with: {api_key[:6]}...")
else:
    print("Failed to load API key from .env")
