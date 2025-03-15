# 🚀 Movie Recommendation System

A FastAPI-powered movie recommendation system that uses KNN and content-based filtering to suggest movies. It leverages TF-IDF, Word2Vec, and multiple features like genre similarity, tags, Bayesian average rating, rating recency, popularity, and release year for precise recommendations. Built with Python, FastAPI, Scikit-learn, Pandas, and Uvicorn.


## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Pandas
- Scikit-learn

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/movie-recommendation-system.git
    cd movie-recommendation-system
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1. Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
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

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

