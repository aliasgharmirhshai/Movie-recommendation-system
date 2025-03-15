# 🚀 Movie Recommendation System

A FastAPI-powered movie recommendation system that uses KNN and content-based filtering to suggest movies. It leverages TF-IDF, Word2Vec, and multiple features like genre similarity, tags, Bayesian average rating, rating recency, popularity, and release year for precise recommendations. Built with Python, FastAPI, Scikit-learn, Pandas, and Uvicorn.

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/movie-recommendation-system.git
    cd movie-recommendation-system
    ```

### Running the Application with Docker

1. Build and start the Docker containers:
    ```bash
    docker-compose up --build
    ```

2. The API will be available at `http://127.0.0.1:8000`.

### API Endpoints

- **Get API status**: `GET /movies/`
- **List all movies**: `GET /movies/all`
- **Get movie by index**: `GET /movies/{index}`
- **Get movie recommendations**: `GET /movies/{index}/recommend`

### Project Structure

- **app/models**: Contains the machine learning models for content-based filtering, collaborative filtering, hybrid recommendation, and deep learning-based models.
- **app/data**: Contains raw and processed data files.
- **app/services**: Contains the core business logic for recommendations, user services, and rating services.
- **app/routers**: Contains the API route definitions.
- **app/main.py**: The main entry point for the FastAPI application.
- **tests**: Contains unit and integration tests.
- **notebooks**: Contains Jupyter notebooks for data analysis and model training.

# Model Preprocessing and Training

## Preprocessing Steps
The model utilizes various preprocessing techniques to prepare the data for recommendations. The genres are transformed into a binary matrix, allowing efficient similarity calculations. Missing values in numerical features such as average ratings, rating counts, and release years are handled by replacing them with the median values for robustness.

To improve feature scaling, different techniques are applied. Rating counts undergo log transformation to handle skewness, followed by normalization. A Bayesian Average Rating is computed to balance popularity and quality. Additionally, rating recency is calculated and normalized to capture user engagement trends.

The release year is also standardized using a min-max scaling approach to ensure consistency in distance-based models.

## Feature Engineering
For textual features, a combination of TF-IDF and Word2Vec is used to encode movie tags. The TF-IDF method extracts important keywords, while Word2Vec generates dense vector representations, allowing the model to capture semantic relationships between movies.

## Model Training
A K-Nearest Neighbors (KNN) algorithm is employed to find similar movies based on feature similarity. The model leverages cosine similarity to measure distances effectively. By incorporating various features such as genres, tag vectors, Bayesian ratings, rating count, rating recency, popularity scores, and release year, the system provides highly relevant recommendations.

The combination of different feature types ensures that the recommendations are both content-based and popularity-aware, making them useful for diverse user preferences.



### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

