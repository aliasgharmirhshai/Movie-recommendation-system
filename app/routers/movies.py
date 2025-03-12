from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import Dict, List, Any, Optional
from pydantic import conint
import logging

from app.models.loader import ModelLoader
from app.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Dependency to get the model loader
def get_model_loader():
    return ModelLoader()

# Dependency to get the recommendation service
def get_recommendation_service(model_loader: ModelLoader = Depends(get_model_loader)):
    return RecommendationService(model_loader)

@router.get("/", summary="Get API status")
async def get_status(model_loader: ModelLoader = Depends(get_model_loader)):
    """Get the API status and model loading information."""
    return model_loader.get_model_status()

@router.get("/all", summary="List all movies")
async def list_all_movies(
    model_loader: ModelLoader = Depends(get_model_loader)
):
    """
    List all movies with their names and IDs.
    
    Returns a list of all movies with their indices and titles.
    """
    try:
        if model_loader.movie_df is None:
            raise HTTPException(status_code=500, detail="Movie data not loaded")
        
        movies_list = model_loader.movie_df[['movieId', 'title']].to_dict(orient='records')
        # Subtract one from each movie ID
        for movie in movies_list:
            movie['movieId'] -= 1
        
        return {"movies": movies_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index}", summary="Get movie by index")
async def get_movie(
    index: conint(ge=0) = Path(..., description="The index of the movie"),
    model_loader: ModelLoader = Depends(get_model_loader)
):
    """
    Get a movie by its index.
    
    Parameters:
    - **index**: The index of the movie
    
    Returns movie details.
    """
    try:
        title = model_loader.get_movie_name(index)
        return {"index": index, "title": title}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving movie: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{index}/recommend", summary="Get movie recommendations")
async def get_recommendations(
    index: conint(ge=0) = Path(..., description="The index of the reference movie"),
    n_neighbors: int = Query(10, ge=1, le=100, description="Number of recommendations"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get movie recommendations based on a reference movie.
    
    Parameters:
    - **index**: The index of the reference movie
    - **n_neighbors**: Number of recommendations to return (default: 10)
    
    Returns similar movies based on features using KNN algorithm.
    """
    try:
        recommended_indices = recommendation_service.get_movie_recommendations(
            index, n_neighbors
        )
        recommendations = recommendation_service.format_recommendations(recommended_indices)
        
        return {
            "input_index": index,
            "input_title": recommendation_service.model_loader.get_movie_name(index),
            "recommendations": recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))