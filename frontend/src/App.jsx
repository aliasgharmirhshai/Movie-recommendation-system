import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import RecommendPage from './pages/RecommendPage';
import AllMoviesPage from './pages/AllMoviesPage';

// Add this for debugging
console.log('App component rendering');

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<AllMoviesPage />} />
          <Route path="/recommend" element={<RecommendPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App; 