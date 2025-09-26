# agent/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Proveedor de modelo
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama")  # ollama or openai
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # API
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", 5))

config = Config()