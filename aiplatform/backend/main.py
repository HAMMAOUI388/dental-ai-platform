from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as ai_router
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str
    BACKEND_HOST: str = "http://localhost:8000"  # default fallback

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# FastAPI instance
app = FastAPI(title="Dental AI API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reports directory (always inside app/reportx
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # => app/
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "app/reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

# Mount /reports -> app/reports
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# Include my AI routes
app.include_router(ai_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from Dental AI!"}



