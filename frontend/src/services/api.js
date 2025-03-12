const BASE_URL = 'http://127.0.0.1:8000';

export const getAllMovies = async (page = 1, limit = 10) => {
  try {
    const response = await fetch(`${BASE_URL}/movies/all?page=${page}&limit=${limit}`);
    return response.json();
  } catch (error) {
    console.error('Error fetching all movies:', error);
    throw error;
  }
};

export const getMovieById = async (id) => {
  const response = await fetch(`${BASE_URL}/movies/${id}`);
  return response.json();
};

export const getRecommendations = async (index) => {
  try {
    const response = await fetch(`${BASE_URL}/movies/${index}/recommend`);
    const data = await response.json();
    console.log('API Response for recommendations:', data); // Debug log
    return data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
}; 