import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getRecommendations, getMovieById } from '../services/api';
import MovieList from '../components/MovieList';

const RecommendPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [movieName, setMovieName] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const index = searchParams.get('index');

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const data = await getRecommendations(index);
        console.log('Received recommendations:', data); // Debug log
        setRecommendations(Array.isArray(data.recommendations) ? data.recommendations : []);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    const fetchMovieName = async () => {
      try {
        const movie = await getMovieById(index);
        setMovieName(movie.title);
      } catch (error) {
        console.error('Error fetching movie details:', error);
      }
    };

    if (index !== null) {
      fetchRecommendations();
      fetchMovieName();
    }
  }, [index]);

  const handleGetRecommendations = (newIndex) => {
    navigate(`/recommend?index=${newIndex}`);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-xl">Loading recommendations...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold mb-8 text-center">Recommended Movies</h2>
      <p className="text-center text-lg mb-4">Recommended for {movieName}</p>
      <MovieList movies={recommendations} onRecommend={handleGetRecommendations} />
    </div>
  );
};

export default RecommendPage; 