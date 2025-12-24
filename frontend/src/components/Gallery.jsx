import React, { useState, useEffect } from 'react';
import { FaTimes, FaTrash, FaDownload, FaImages } from 'react-icons/fa';
import api from '../services/api';
import './Gallery.css';

const Gallery = ({ onClose }) => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    fetchGallery();
  }, []);

  const fetchGallery = async () => {
    try {
      setLoading(true);
      const response = await api.getGallery();
      if (response.data.success) {
        setImages(response.data.data.images);
      }
    } catch (err) {
      console.error('Error fetching gallery:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await api.deleteFromGallery(filename);
        setImages(images.filter(img => img.filename !== filename));
        setSelectedImage(null);
      } catch (err) {
        console.error('Error deleting image:', err);
        alert('Failed to delete image');
      }
    }
  };

  const handleDownload = (filename) => {
    const link = document.createElement('a');
    link.href = api.getImageUrl(filename);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="gallery-overlay">
      <div className="gallery-modal">
        <div className="gallery-header">
          <div className="gallery-title-section">
            <FaImages className="gallery-icon" />
            <h2 className="gallery-title">Gallery</h2>
            <span className="image-count">{images.length} images</span>
          </div>
          <button className="close-btn" onClick={onClose}>
            <FaTimes />
          </button>
        </div>

        <div className="gallery-content">
          {loading ? (
            <div className="gallery-loading">
              <div className="spinner"></div>
              <p>Loading gallery...</p>
            </div>
          ) : images.length === 0 ? (
            <div className="gallery-empty">
              <FaImages className="empty-gallery-icon" />
              <h3>No images yet</h3>
              <p>Your generated images will appear here</p>
            </div>
          ) : (
            <div className="gallery-grid">
              {images.map((image) => (
                <div
                  key={image.filename}
                  className="gallery-item"
                  onClick={() => setSelectedImage(image)}
                >
                  <img
                    src={api.getImageUrl(image.filename)}
                    alt={image.filename}
                    className="gallery-thumbnail"
                  />
                  <div className="gallery-item-overlay">
                    <div className="overlay-actions">
                      <button
                        className="overlay-btn download-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(image.filename);
                        }}
                      >
                        <FaDownload />
                      </button>
                      <button
                        className="overlay-btn delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(image.filename);
                        }}
                      >
                        <FaTrash />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Image Preview Modal */}
        {selectedImage && (
          <div className="image-preview-overlay" onClick={() => setSelectedImage(null)}>
            <div className="image-preview-content" onClick={(e) => e.stopPropagation()}>
              <button
                className="preview-close"
                onClick={() => setSelectedImage(null)}
              >
                <FaTimes />
              </button>
              <img
                src={api.getImageUrl(selectedImage.filename)}
                alt={selectedImage.filename}
                className="preview-image"
              />
              <div className="preview-actions">
                <button
                  className="btn btn-success"
                  onClick={() => handleDownload(selectedImage.filename)}
                >
                  <FaDownload /> Download
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => handleDelete(selectedImage.filename)}
                >
                  <FaTrash /> Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Gallery;