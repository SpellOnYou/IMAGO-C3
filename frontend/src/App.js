import React, { useState } from 'react';
import { fetchPhotos } from './api';
import './App.css';

function App() {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useState({
    title: '',
    bildnummer: '',
    description: '',
    suchtext: '',
    date_from: '',
    date_to: ''
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  });

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await fetchPhotos({ ...searchParams, page: pagination.currentPage, page_size: pagination.pageSize });
      setPhotos(data.photos);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        totalPages: data.total_pages
      }));
      // Clear search parameters after successful search
      setSearchParams({
        title: '',
        bildnummer: '',
        description: '',
        suchtext: '',
        date_from: '',
        date_to: ''
      });
    } catch (error) {
      console.error('Error searching photos:', error);
    }
    setLoading(false);
  };

  const handlePageChange = async (newPage) => {
    setLoading(true);
    try {
      const data = await fetchPhotos({ ...searchParams, page: newPage, page_size: pagination.pageSize });
      setPhotos(data.photos);
      setPagination(prev => ({
        ...prev,
        currentPage: newPage,
        total: data.total,
        totalPages: data.total_pages
      }));
    } catch (error) {
      console.error('Error fetching page:', error);
    }
    setLoading(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getImageUrl = (photo) => {
    console.log("photo", photo)
    const mediaId = photo.mediaId.padStart(10, '0');
    const db = photo.db ? photo.db.slice(0, 2) : 'st'; // Default to 'st' if db is not specified; 
    return `https://www.imago-images.de/bild/${db}/${mediaId}/s.jpg`;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Imago - Coding Challenge C3</h1>
      </header>

      <div className="search-container">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-group">
            <label htmlFor="title">Title:</label>
            <input
              type="text"
              id="title"
              name="title"
              value={searchParams.title}
              onChange={handleInputChange}
              placeholder="Enter title"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <input
              type="text"
              id="description"
              name="description"
              value={searchParams.description}
              onChange={handleInputChange}
              placeholder="Enter description"
            />
          </div>

          <div className="form-group">
            <label htmlFor="suchtext">Search Text:</label>
            <input
              type="text"
              id="suchtext"
              name="suchtext"
              value={searchParams.suchtext}
              onChange={handleInputChange}
              placeholder="Enter search text"
            />
          </div>

          <div className="form-group">
            <label htmlFor="date_from">Date Range:</label>
            <div className="date-range">
              <input
                type="date"
                id="date_from"
                name="date_from"
                value={searchParams.date_from}
                onChange={handleInputChange}
              />
              <span>to</span>
              <input
                type="date"
                id="date_to"
                name="date_to"
                value={searchParams.date_to}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="bildnummer">Bildnummer:</label>
            <input
              type="text"
              id="bildnummer"
              name="bildnummer"
              value={searchParams.bildnummer}
              onChange={handleInputChange}
              placeholder="Enter image number"
            />
          </div>

          <button type="submit">Search</button>
        </form>
      </div>

      {loading ? (
        <div className="loading">👋</div>
      ) : (
        <>
          <div className="photo-grid">
            {photos.map((photo) => (
              <div key={photo.id} className="photo-card">
                <img 
                  src={getImageUrl(photo)}
                  alt={photo.title}
                  loading="lazy"
                />
                <div className="photo-info">
                  <p><strong>Title:</strong> {photo.title}</p>
                  <p><strong>Date:</strong> {new Date(photo.date).toLocaleDateString()}</p>
                  <p><strong>Description:</strong> {photo.description}</p>
                  <p><strong>Media ID (Bildnummer):</strong> {photo.mediaId}</p>
                  <p><strong>Database:</strong> {photo.db}</p>
                  <p><strong>Keywords:</strong> {photo.keywords}</p>
                </div>
              </div>
            ))}
          </div>
          
          {pagination.totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(pagination.currentPage - 1)}
                disabled={pagination.currentPage === 1}
              >
                Previous
              </button>
              <span>
                Page {pagination.currentPage} of {pagination.totalPages}
              </span>
              <button 
                onClick={() => handlePageChange(pagination.currentPage + 1)}
                disabled={pagination.currentPage === pagination.totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
