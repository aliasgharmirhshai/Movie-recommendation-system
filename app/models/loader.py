import pickle
import logging
import pandas as pd
from typing import Dict, List, Any, Tuple
import os
from pathlib import Path
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    """Responsible for loading and managing ML models and datasets."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            # Initialize instance variables
            cls._instance.knn = None
            cls._instance.tfidf = None
            cls._instance.tag_vectors = None
            cls._instance.features = None
            cls._instance.movie_names = None
            cls._instance.movie_df = None
        return cls._instance
    
    def load_models(self) -> None:
        """Load all required ML models from disk."""
        model_dir = settings.MODEL_DIR
        
        try:
            # Check if models directory exists
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
            model_files = {
                "knn_model.pkl": "knn",
                "tfidf_model.pkl": "tfidf",
                "tag_vectors.pkl": "tag_vectors",
                "features.pkl": "features"
            }
            
            for filename, attr_name in model_files.items():
                file_path = Path(model_dir) / filename
                if not file_path.exists():
                    raise FileNotFoundError(f"Model file not found: {file_path}")
                
                logger.info(f"Loading model from {file_path}")
                with open(file_path, "rb") as f:
                    setattr(self, attr_name, pickle.load(f))
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load models: {str(e)}")
    
    def load_dataset(self) -> None:
        """Load the movie dataset and extract relevant information."""
        csv_path = Path(settings.DATA_DIR) / settings.DATASET_PATH
        
        try:
            if not csv_path.exists():
                raise FileNotFoundError(f"Dataset file not found: {csv_path}")
            
            logger.info(f"Loading dataset from {csv_path}")
            self.movie_df = pd.read_csv(csv_path)
            
            if "title" not in self.movie_df.columns:
                raise ValueError("CSV file does not contain a 'title' column")
            
            self.movie_names = self.movie_df["title"].tolist()
            logger.info(f"Loaded {len(self.movie_names)} movie titles")
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load dataset: {str(e)}")
    
    def get_movie_name(self, idx: int) -> str:
        """Get movie title by index with validation."""
        if self.movie_names is None:
            raise HTTPException(status_code=500, detail="Movie data not loaded")
            
        if not 0 <= idx < len(self.movie_names):
            raise HTTPException(status_code=404, detail=f"Movie index {idx} out of bounds")
            
        return self.movie_names[idx]
    
    def get_model_status(self) -> Dict[str, bool]:
        """Return loading status of all models and data."""
        return {
            "knn_loaded": self.knn is not None,
            "tfidf_loaded": self.tfidf is not None,
            "tag_vectors_loaded": self.tag_vectors is not None,
            "features_loaded": self.features is not None,
            "movie_data_loaded": self.movie_names is not None,
            "total_movies": len(self.movie_names) if self.movie_names else 0
        }