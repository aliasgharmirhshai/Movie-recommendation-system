import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings and configurations."""
    # Model and data paths
    MODEL_DIR: str = os.getenv("MODEL_DIR", "./models")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data/processed")
    DATASET_PATH: str = os.getenv("DATASET_PATH", "combined_movie_data.csv")
    
    # Server configurations
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8080))
    
    # API configurations
    API_TITLE: str = "Movie Recommendation API"
    API_DESCRIPTION: str = "API for movie recommendations using KNN algorithm"
    API_VERSION: str = "1.0.0"
    
    # Performance configurations
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()