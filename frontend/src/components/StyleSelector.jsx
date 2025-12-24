import React, { useState, useEffect } from 'react';
import { FaPalette } from 'react-icons/fa';
import api from '../services/api';
import './StyleSelector.css';

const StyleSelector = ({ onSelectStyle, selectedStyle, disabled }) => {
  const [styles, setStyles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStyles();
  }, []);

  const fetchStyles = async () => {
    try {
      const response = await api.getStyles();
      if (response.data.success) {
        setStyles(response.data.data.styles);
      }
    } catch (err) {
      console.error('Error fetching styles:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="style-selector">
        <div className="selector-header">
          <FaPalette className="header-icon" />
          <h3 className="selector-title">Select Style</h3>
        </div>
        <div className="loading-styles">Loading styles...</div>
      </div>
    );
  }

  return (
    <div className="style-selector">
      <div className="selector-header">
        <FaPalette className="header-icon" />
        <h3 className="selector-title">Select Style Preset</h3>
      </div>
      
      <div className="styles-grid">
        {styles.map((style) => (
          <div
            key={style.id}
            className={`style-card ${selectedStyle?.id === style.id ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onSelectStyle(style)}
          >
            <div className="style-thumbnail">
              <div className="style-placeholder">
                <FaPalette />
              </div>
            </div>
            <div className="style-info">
              <h4 className="style-name">{style.name}</h4>
              <p className="style-description">{style.description}</p>
            </div>
            {selectedStyle?.id === style.id && (
              <div className="selected-badge">✓</div>
            )}
          </div>
        ))}
      </div>

      {styles.length === 0 && (
        <div className="no-styles">
          <p>No style presets available</p>
        </div>
      )}
    </div>
  );
};

export default StyleSelector;