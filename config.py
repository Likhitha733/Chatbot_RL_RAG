import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    
    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    # Increased to 15 to ensure we get full lists/chapters
    TOP_K_RESULTS = 15
    
    # Paths
    PDF_PATH = "./budget_speech.pdf"
    CHROMA_PATH = "./chroma_db"
    FEEDBACK_FILE = "./data/feedback_history.json"