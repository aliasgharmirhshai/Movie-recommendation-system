import numpy as np
from typing import List, Dict, Any, Optional
import logging
from fastapi import HTTPException
from functools import lru_cache

from app.models.loader import ModelLoader

logger = logging.getLogger(__name__)

class RecommendationService:
    """Service for handling movie recommendation logic."""
    
    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader
    
    def validate_movie_index(self, index: int) -> None:
        """Validate if the movie index is within bounds."""
        if self.model_loader.features is None:
            raise HTTPException(status_code=500, detail="Feature data not loaded")
            
        if not 0 <= index < len(self.model_loader.features):
            raise HTTPException(
                status_code=404, 
                detail=f"Movie index {index} out of bounds (max: {len(self.model_loader.features)-1})"
            )
    
    @lru_cache(maxsize=1000)
    def get_movie_recommendations(self, movie_index: int, n_neighbors: int = 10) -> List[int]:
        """
        Get movie recommendations based on KNN model.
        
        Args:
            movie_index: Index of the target movie
            n_neighbors: Number of similar movies to find
            
        Returns:
            List of recommended movie indices
        """
        try:
            self.validate_movie_index(movie_index)
            
            # Get the features for the requested movie
            movie_features = self.model_loader.features[movie_index].reshape(1, -1)
            
            # Find similar movies using KNN
            distances, indices = self.model_loader.knn.kneighbors(
                movie_features, 
                n_neighbors=min(n_neighbors + 1, len(self.model_loader.features))
            )
            
            # Remove the input movie from recommendations (usually the first result)
            recommended_indices = [
                int(idx) for idx in indices[0] 
                if idx != movie_index
            ][:n_neighbors]
            
            return recommended_indices
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate recommendations: {str(e)}"
            )
    
    def format_recommendations(self, indices: List[int]) -> List[Dict[str, Any]]:
        """Format recommendation indices into detailed response objects."""
        recommendations = []
        
        for idx in indices:
            try:
                title = self.model_loader.get_movie_name(idx)
                recommendations.append({
                    "index": idx,
                    "title": title
                })
            except HTTPException as e:
                logger.warning(f"Skipping invalid movie index {idx}: {str(e)}")
                
        return recommendations