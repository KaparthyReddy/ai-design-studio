import React, { useState } from 'react';
import { FaMagic, FaPlus, FaTimes } from 'react-icons/fa';
import './StyleMixer.css';

const StyleMixer = ({ onMixStyles, disabled }) => {
  const [styles, setStyles] = useState([
    { id: 1, weight: 0.5, name: 'Style 1' }
  ]);

  const addStyle = () => {
    if (styles.length < 4) {
      setStyles([
        ...styles,
        { id: Date.now(), weight: 0.5, name: `Style ${styles.length + 1}` }
      ]);
    }
  };

  const removeStyle = (id) => {
    if (styles.length > 1) {
      setStyles(styles.filter(s => s.id !== id));
    }
  };

  const updateWeight = (id, weight) => {
    setStyles(styles.map(s => 
      s.id === id ? { ...s, weight: parseFloat(weight) } : s
    ));
  };

  const normalizeWeights = () => {
    const total = styles.reduce((sum, s) => sum + s.weight, 0);
    return styles.map(s => ({ ...s, weight: s.weight / total }));
  };

  const handleMix = () => {
    const normalized = normalizeWeights();
    onMixStyles(normalized);
  };

  return (
    <div className="style-mixer">
      <div className="mixer-header">
        <FaMagic className="mixer-icon" />
        <h3 className="mixer-title">Style Mixer</h3>
        <span className="beta-badge">BETA</span>
      </div>

      <p className="mixer-description">
        Blend multiple styles together by adjusting their weights
      </p>

      <div className="styles-list">
        {styles.map((style, index) => (
          <div key={style.id} className="style-item">
            <div className="style-header">
              <span className="style-label">{style.name}</span>
              {styles.length > 1 && (
                <button
                  className="remove-btn"
                  onClick={() => removeStyle(style.id)}
                  disabled={disabled}
                >
                  <FaTimes />
                </button>
              )}
            </div>
            
            <div className="weight-control">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={style.weight}
                onChange={(e) => updateWeight(style.id, e.target.value)}
                className="slider"
                disabled={disabled}
              />
              <span className="weight-value">{(style.weight * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mixer-actions">
        <button
          className="btn btn-secondary"
          onClick={addStyle}
          disabled={disabled || styles.length >= 4}
          style={{ width: '100%' }}
        >
          <FaPlus /> Add Style {styles.length < 4 ? `(${4 - styles.length} left)` : '(Max)'}
        </button>

        <button
          className="btn btn-primary"
          onClick={handleMix}
          disabled={disabled}
          style={{ width: '100%', marginTop: '0.75rem' }}
        >
          <FaMagic /> Mix Styles
        </button>
      </div>

      <div className="mixer-info">
        <p>💡 Weights will be automatically normalized to sum to 100%</p>
      </div>
    </div>
  );
};

export default StyleMixer;