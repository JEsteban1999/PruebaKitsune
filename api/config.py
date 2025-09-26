import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "cannabis_licencias.db")
    API_KEY: str = os.getenv("API_KEY", "cannabis-key-2025")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"

settings = Settings()