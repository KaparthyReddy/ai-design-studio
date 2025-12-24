import React from 'react';
import { FaDownload, FaUndo, FaImage } from 'react-icons/fa';
import LoadingSpinner from './LoadingSpinner';
import './ImageCanvas.css';

const ImageCanvas = ({ 
  contentImage, 
  styleImage, 
  resultImage, 
  isProcessing,
  processingProgress,
  onDownload,
  onReset 
}) => {
  
  if (!contentImage && !styleImage && !resultImage) {
    return (
      <div className="canvas-empty">
        <div className="empty-state">
          <FaImage className="empty-icon" />
          <h2 className="empty-title">No Images Yet</h2>
          <p className="empty-description">
            Upload a content image and a style image to get started with AI-powered style transfer
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="image-canvas">
      <div className="canvas-header">
        <h2 className="canvas-title">
          {isProcessing ? '🎨 Processing...' : resultImage ? '✨ Result' : '📸 Preview'}
        </h2>
        {resultImage && !isProcessing && (
          <div className="canvas-actions">
            <button className="btn btn-success" onClick={onDownload}>
              <FaDownload /> Download
            </button>
            <button className="btn btn-secondary" onClick={onReset}>
              <FaUndo /> New
            </button>
          </div>
        )}
      </div>

      <div className="canvas-grid">
        {/* Content Image */}
        {contentImage && (
          <div className="canvas-item fade-in">
            <div className="canvas-label">Content Image</div>
            <div className="canvas-image-wrapper">
              <img 
                src={contentImage.preview} 
                alt="Content" 
                className="canvas-image"
              />
            </div>
          </div>
        )}

        {/* Style Image */}
        {styleImage && (
          <div className="canvas-item fade-in">
            <div className="canvas-label">Style Image</div>
            <div className="canvas-image-wrapper">
              <img 
                src={styleImage.preview} 
                alt="Style" 
                className="canvas-image"
              />
            </div>
          </div>
        )}

        {/* Result or Processing */}
        {(isProcessing || resultImage) && (
          <div className="canvas-item canvas-result fade-in">
            <div className="canvas-label">
              {isProcessing ? 'Processing...' : 'Result'}
              {resultImage && resultImage.processingTime && (
                <span className="processing-time">
                  ⚡ {resultImage.processingTime}
                </span>
              )}
            </div>
            <div className="canvas-image-wrapper">
              {isProcessing ? (
                <div className="processing-overlay">
                  <LoadingSpinner />
                  <p className="processing-text">Applying neural style transfer...</p>
                  {processingProgress > 0 && (
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${processingProgress}%` }}
                      />
                    </div>
                  )}
                </div>
              ) : (
                <img 
                  src={resultImage.url} 
                  alt="Result" 
                  className="canvas-image result-image"
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Processing Info */}
      {isProcessing && (
        <div className="processing-info">
          <p>⏳ This may take 1-3 minutes depending on image size and quality settings</p>
        </div>
      )}
    </div>
  );
};

export default ImageCanvas;