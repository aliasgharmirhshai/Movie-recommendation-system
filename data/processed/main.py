import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_cleaning.log'
)

def load_data():
    """Load all datasets and display their basic information."""
    logging.info("Loading datasets...")
    
    datasets = {
        'movies': pd.read_csv("../raw/movies.csv"),
        'ratings': pd.read_csv('../raw/ratings.csv'),
        'tags': pd.read_csv('../raw/tags.csv'),
        'links': pd.read_csv('../raw/links.csv')
    }
    
    for name, df in datasets.items():
        logging.info(f"\n{name.upper()} Dataset:")
        logging.info(f"Shape: {df.shape}")
        logging.info(f"Columns: {df.columns.tolist()}")
        logging.info(f"Data Types:\n{df.dtypes}")
        logging.info(f"Missing Values:\n{df.isnull().sum()}")
    
    return datasets

def handle_missing_values(datasets):
    """Handle missing values in all datasets."""
    logging.info("Handling missing values...")
    
    # Handle movies dataset
    if datasets['movies']['genres'].isnull().any():
        datasets['movies']['genres'] = datasets['movies']['genres'].fillna('Unknown')
    
    # Handle ratings dataset - drop rows with missing ratings
    datasets['ratings'].dropna(subset=['rating'], inplace=True)
    
    # Handle tags dataset - drop rows with missing tags
    datasets['tags'].dropna(subset=['tag'], inplace=True)
    
    # Handle links dataset - fill missing IDs with -1
    datasets['links'] = datasets['links'].fillna(-1)
    
    return datasets

def remove_duplicates(datasets):
    """Remove duplicate entries from all datasets."""
    logging.info("Removing duplicates...")
    
    for name, df in datasets.items():
        initial_rows = len(df)
        if name == 'ratings':
            # Keep the latest rating for each user-movie pair
            df = df.sort_values('timestamp').drop_duplicates(
                subset=['userId', 'movieId'], 
                keep='last'
            )
        elif name == 'tags':
            # Keep the latest tag for each user-movie pair
            df = df.sort_values('timestamp').drop_duplicates(
                subset=['userId', 'movieId', 'tag'], 
                keep='last'
            )
        else:
            df = df.drop_duplicates()
        
        datasets[name] = df
        removed = initial_rows - len(df)
        logging.info(f"Removed {removed} duplicates from {name} dataset")
    
    return datasets

def convert_data_types(datasets):
    """Convert data types and handle timestamps."""
    logging.info("Converting data types...")
    
    # Convert timestamps to datetime
    for df in [datasets['ratings'], datasets['tags']]:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['day'] = df['timestamp'].dt.day
    
    # Convert IDs to integers
    for name, df in datasets.items():
        if 'movieId' in df.columns:
            df['movieId'] = df['movieId'].astype(int)
        if 'userId' in df.columns:
            df['userId'] = df['userId'].astype(int)
    
    # Convert links IDs to integers
    datasets['links']['imdbId'] = datasets['links']['imdbId'].astype(int)
    datasets['links']['tmdbId'] = datasets['links']['tmdbId'].astype(int)
    
    return datasets

def handle_outliers(datasets):
    """Detect and handle outliers in numerical features."""
    logging.info("Handling outliers...")
    
    # Handle rating outliers
    ratings = datasets['ratings']
    q1 = ratings['rating'].quantile(0.25)
    q3 = ratings['rating'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Cap outliers instead of removing them
    datasets['ratings']['rating'] = ratings['rating'].clip(lower_bound, upper_bound)
    
    return datasets

def standardize_and_encode(datasets):
    """Standardize numerical features and encode categorical features."""
    logging.info("Standardizing and encoding features...")
    
    # Normalize ratings to 0-1 scale
    ratings = datasets['ratings']
    ratings['normalized_rating'] = (ratings['rating'] - ratings['rating'].min()) / \
                                 (ratings['rating'].max() - ratings['rating'].min())
    
    # One-hot encode genres
    movies = datasets['movies']
    genres_list = movies['genres'].str.split('|').explode().unique()
    for genre in genres_list:
        movies[f'genre_{genre}'] = movies['genres'].str.contains(genre).astype(int)
    
    return datasets

def extract_features(datasets):
    """Extract and engineer new features."""
    logging.info("Extracting features...")
    
    # Extract release year from movie title
    datasets['movies']['release_year'] = datasets['movies']['title'].str.extract(r'\((\d{4})\)').astype(float)
    
    # Compute rating statistics per movie
    rating_stats = datasets['ratings'].groupby('movieId').agg({
        'rating': ['count', 'mean', 'std']
    }).reset_index()
    rating_stats.columns = ['movieId', 'rating_count', 'average_rating', 'rating_std']
    
    # Merge rating statistics with movies dataset
    datasets['movies'] = datasets['movies'].merge(rating_stats, on='movieId', how='left')
    
    return datasets

def validate_and_save(datasets):
    """Perform final validation and save cleaned datasets."""
    logging.info("Validating and saving cleaned datasets...")
    
    # Create processed directory if it doesn't exist
    os.makedirs('../processed', exist_ok=True)
    
    # Final validation and saving
    for name, df in datasets.items():
        # Check for missing values
        missing = df.isnull().sum().sum()
        logging.info(f"Missing values in {name} dataset: {missing}")
        
        # Save cleaned dataset
        output_path = f'../processed/cleaned_{name}.csv'
        df.to_csv(output_path, index=False)
        logging.info(f"Saved cleaned {name} dataset to {output_path}")
    
    return True

def combine_datasets(datasets):
    """Combine all cleaned datasets into a single comprehensive dataset."""
    logging.info("Combining all datasets into a single file...")
    
    # Start with movies as the base
    combined_df = datasets['movies'].copy()
    
    # Add average rating information
    ratings_agg = datasets['ratings'].groupby('movieId').agg({
        'rating': ['count', 'mean', 'std', 'min', 'max'],
        'normalized_rating': ['mean', 'std'],
        'year': ['min', 'max']  # First and last rating dates
    }).reset_index()
    
    # Flatten column names
    ratings_agg.columns = ['movieId', 'total_ratings', 'avg_rating', 'rating_std',
                          'min_rating', 'max_rating', 'avg_normalized_rating',
                          'normalized_rating_std', 'first_rating_year', 'last_rating_year']
    
    # Combine tags for each movie
    tags_agg = datasets['tags'].groupby('movieId')['tag'].agg(lambda x: '|'.join(x)).reset_index()
    tags_agg.columns = ['movieId', 'all_tags']
    
    # Count number of unique tags per movie
    tags_count = datasets['tags'].groupby('movieId')['tag'].nunique().reset_index()
    tags_count.columns = ['movieId', 'num_unique_tags']
    
    # Add external IDs from links
    links_df = datasets['links']
    
    # Merge all information
    combined_df = combined_df.merge(ratings_agg, on='movieId', how='left')
    combined_df = combined_df.merge(tags_agg, on='movieId', how='left')
    combined_df = combined_df.merge(tags_count, on='movieId', how='left')
    combined_df = combined_df.merge(links_df, on='movieId', how='left')
    
    # Fill missing values appropriately
    combined_df['all_tags'] = combined_df['all_tags'].fillna('no_tags')
    combined_df['num_unique_tags'] = combined_df['num_unique_tags'].fillna(0)
    
    # Add some additional metrics
    combined_df['has_tags'] = (combined_df['num_unique_tags'] > 0).astype(int)
    combined_df['rating_popularity'] = (combined_df['total_ratings'] - combined_df['total_ratings'].min()) / \
                                     (combined_df['total_ratings'].max() - combined_df['total_ratings'].min())
    
    # Save the combined dataset
    output_path = '../processed/combined_movie_data.csv'
    combined_df.to_csv(output_path, index=False)
    logging.info(f"Saved combined dataset to {output_path}")
    
    # Log some statistics about the combined dataset
    logging.info(f"Combined dataset shape: {combined_df.shape}")
    logging.info(f"Number of features: {len(combined_df.columns)}")
    logging.info("Features included: " + ", ".join(combined_df.columns))
    
    return combined_df

def main():
    """Main function to orchestrate the data cleaning pipeline."""
    logging.info("Starting data cleaning pipeline...")
    
    # Load data
    datasets = load_data()
    
    # Apply cleaning steps
    datasets = handle_missing_values(datasets)
    datasets = remove_duplicates(datasets)
    datasets = convert_data_types(datasets)
    datasets = handle_outliers(datasets)
    datasets = standardize_and_encode(datasets)
    datasets = extract_features(datasets)
    
    # Save individual cleaned datasets
    validate_and_save(datasets)
    
    # Create and save combined dataset
    combined_df = combine_datasets(datasets)
    
    logging.info("Data cleaning pipeline completed successfully!")

if __name__ == "__main__":
    main()