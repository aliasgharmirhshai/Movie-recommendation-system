const MovieCard = ({ title, onRecommend }) => {
  return (
    <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg text-gray-800">{title}</h3>
      <button
        onClick={onRecommend}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Recommend
      </button>
    </div>
  );
};

export default MovieCard; 