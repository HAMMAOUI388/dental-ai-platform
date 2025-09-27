
from pydantic_settings import BaseSettings
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  #points to app/

class Settings(BaseSettings):
    # Required
    DATABASE_URL: str

    # Model paths
    DETECTION_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "../models/detect.pt")
    NUMBERING_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "../models/numbering.pt")

    # Reports directory
    REPORTS_DIR: str = os.path.join(BASE_DIR, "reports")  #this folder created locally

    # optional (frontend only)
    NEXT_PUBLIC_API_URL: str | None = None

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../.env")
        
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings()