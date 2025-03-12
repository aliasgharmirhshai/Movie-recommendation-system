import MovieCard from './MovieCard';

const MovieList = ({ movies, onRecommend }) => {
  if (!Array.isArray(movies)) {
    console.error('Expected movies to be an array, but got:', movies);
    return <div className="text-center text-red-500">No movies available</div>; // Fallback UI
  }

  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {movies.map((movie, index) => (
        <MovieCard
          key={index}
          title={movie.title}
          onRecommend={() => onRecommend(index)}
        />
      ))}
    </div>
  );
};

export default MovieList; 