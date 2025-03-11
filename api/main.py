from fastapi import FastAPI, HTTPException
import pickle
import pandas as pd
import numpy as np

app = FastAPI()

# Global variables to hold loaded models and data
knn = None
tfidf = None
tag_vectors = None
features = None
movie_names = None

@app.on_event("startup")
def load_models_and_data():
    """
    Loads the machine learning models and dataset at startup.
    """
    global knn, tfidf, tag_vectors, features, movie_names

    # Update this path to where your models are stored
    model_dir = "./models"  
    try:
        with open(f"{model_dir}/knn_model.pkl", "rb") as f:
            knn = pickle.load(f)
        with open(f"{model_dir}/tfidf_model.pkl", "rb") as f:
            tfidf = pickle.load(f)
        with open(f"{model_dir}/tag_vectors.pkl", "rb") as f:
            tag_vectors = pickle.load(f)
        with open(f"{model_dir}/features.pkl", "rb") as f:
            features = pickle.load(f)
    except Exception as e:
        raise Exception(f"Error loading models: {e}")

    # Load movie names from the CSV dataset
    csv_path = "./data/processed/combined_movie_data.csv"
    try:
        df = pd.read_csv(csv_path)
        if "title" not in df.columns:
            raise Exception("CSV file does not contain a 'title' column.")
        movie_names = df["title"].tolist()
    except Exception as e:
        raise Exception(f"Error loading dataset: {e}")

def get_movie_name(idx: int) -> str:
    """
    Returns the movie title for the given index.
    Raises HTTPException if index is out of bounds.
    """
    if idx < 0 or idx >= len(movie_names):
        raise HTTPException(status_code=404, detail="Index out of bounds")
    return movie_names[idx]

def recommend_movies(movie_index: int, n_neighbors: int = 10) -> np.ndarray:
    """
    Uses the KNN model to retrieve recommended movie indices for a given movie index.
    """
    # Reshape the feature vector to match expected KNN input
    movie_features = features[movie_index].reshape(1, -1)
    distances, indices = knn.kneighbors(movie_features, n_neighbors=n_neighbors)
    return indices[0]  # Return flattened array of indices

@app.get("/movie/{index}")
def read_movie(index: int):
    """
    Endpoint to retrieve the movie title given its index.
    """
    try:
        title = get_movie_name(index)
        return {"index": index, "title": title}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{index}")
def get_recommendations(index: int, n_neighbors: int = 10):
    """
    Endpoint to get movie recommendations for a given movie index.
    Returns both the indices and titles of recommended movies.
    """
    if index < 0 or index >= len(features):
        raise HTTPException(status_code=404, detail="Index out of bounds")
    
    recommended_indices = recommend_movies(index, n_neighbors=n_neighbors)
    recommendations = []
    for idx in recommended_indices:
        recommendations.append({
            "index": int(idx),
            "title": get_movie_name(idx)
        })
    
    return {"input_index": index, "recommendations": recommendations}

# To run the API using Uvicorn:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
