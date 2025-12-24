import React, { useState, useEffect } from 'react';
import './App.css';
import { FaPalette, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

import ImageUploader from './components/ImageUploader';
import StyleSelector from './components/StyleSelector';
import ImageCanvas from './components/ImageCanvas';
import StyleMixer from './components/StyleMixer';
import Gallery from './components/Gallery';
import LoadingSpinner from './components/LoadingSpinner';

import api from './services/api';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [contentImage, setContentImage] = useState(null);
  const [styleImage, setStyleImage] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [styleIntensity, setStyleIntensity] = useState(1.0);
  const [quality, setQuality] = useState('standard');
  const [error, setError] = useState(null);
  const [showGallery, setShowGallery] = useState(false);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await api.checkHealth();
      setBackendStatus('online');
      console.log('✅ Backend is online:', response.data);
    } catch (err) {
      setBackendStatus('offline');
      console.error('❌ Backend is offline:', err);
    }
  };

  const handleContentUpload = async (file) => {
    try {
      setError(null);
      const response = await api.uploadImage(file);
      setContentImage({
        filename: response.data.data.filename,
        path: response.data.data.path,
        preview: URL.createObjectURL(file)
      });
      console.log('✅ Content image uploaded:', response.data);
    } catch (err) {
      setError('Failed to upload content image: ' + err.message);
      console.error('Error uploading content:', err);
    }
  };

  const handleStyleUpload = async (file) => {
    try {
      setError(null);
      const response = await api.uploadImage(file);
      setStyleImage({
        filename: response.data.data.filename,
        path: response.data.data.path,
        preview: URL.createObjectURL(file)
      });
      console.log('✅ Style image uploaded:', response.data);
    } catch (err) {
      setError('Failed to upload style image: ' + err.message);
      console.error('Error uploading style:', err);
    }
  };

  const handleStyleTransfer = async (quickMode = false) => {
    if (!contentImage || !styleImage) {
      setError('Please upload both content and style images');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      setProcessingProgress(0);

      console.log('🎨 Starting style transfer...');
      console.log('Quality:', quality);
      console.log('Intensity:', styleIntensity);
      console.log('Quick mode:', quickMode);

      const response = quickMode
        ? await api.quickTransfer({
            content_image: contentImage.path,
            style_image: styleImage.path,
            intensity: styleIntensity
          })
        : await api.styleTransfer({
            content_image: contentImage.path,
            style_image: styleImage.path,
            intensity: styleIntensity,
            quality: quality
          });

      if (response.data.success) {
        const imageUrl = api.getImageUrl(response.data.data.output_image);
        setResultImage({
          filename: response.data.data.output_image,
          url: imageUrl,
          processingTime: response.data.data.processing_time
        });
        setProcessingProgress(100);
        console.log('✅ Style transfer complete!');
      }
    } catch (err) {
      setError('Style transfer failed: ' + err.message);
      console.error('Error in style transfer:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setContentImage(null);
    setStyleImage(null);
    setResultImage(null);
    setError(null);
    setProcessingProgress(0);
  };

  const handleDownload = () => {
    if (resultImage) {
      const link = document.createElement('a');
      link.href = resultImage.url;
      link.download = resultImage.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="app-logo">
            <FaPalette className="logo-icon" />
            <div>
              <h1 className="app-title">AI Design Studio</h1>
              <p className="app-subtitle">Neural Style Transfer with GANs</p>
            </div>
          </div>
          <div className="header-actions">
            <div className={`status-badge ${backendStatus}`}>
              <span className="status-dot"></span>
              {backendStatus === 'online' ? (
                <>
                  <FaCheckCircle /> Backend Online
                </>
              ) : backendStatus === 'offline' ? (
                <>
                  <FaTimesCircle /> Backend Offline
                </>
              ) : (
                'Checking...'
              )}
            </div>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowGallery(!showGallery)}
            >
              {showGallery ? 'Hide Gallery' : 'Show Gallery'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {error && (
          <div className="error-banner fade-in" style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid var(--error-color)',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            color: 'var(--error-color)'
          }}>
            ⚠️ {error}
          </div>
        )}

        {showGallery ? (
          <Gallery onClose={() => setShowGallery(false)} />
        ) : (
          <div className="workspace">
            {/* Canvas Area */}
            <div className="canvas-area">
              <ImageCanvas
                contentImage={contentImage}
                styleImage={styleImage}
                resultImage={resultImage}
                isProcessing={isProcessing}
                processingProgress={processingProgress}
                onDownload={handleDownload}
                onReset={handleReset}
              />
            </div>

            {/* Controls Panel */}
            <div className="controls-panel">
              <h2 className="section-title">
                <span className="section-icon">⚙️</span>
                Controls
              </h2>

              {/* Upload Section */}
              <div className="control-section">
                <h3 className="control-title">1. Upload Images</h3>
                <ImageUploader
                  label="Content Image"
                  onUpload={handleContentUpload}
                  currentImage={contentImage}
                  disabled={isProcessing}
                />
                <div style={{ marginTop: '1rem' }}>
                  <ImageUploader
                    label="Style Image"
                    onUpload={handleStyleUpload}
                    currentImage={styleImage}
                    disabled={isProcessing}
                  />
                </div>
              </div>

              {/* Style Controls */}
              <div className="control-section" style={{ marginTop: '1.5rem' }}>
                <h3 className="control-title">2. Adjust Settings</h3>
                
                <div className="input-group">
                  <label className="input-label">
                    Style Intensity: {styleIntensity.toFixed(1)}x
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    value={styleIntensity}
                    onChange={(e) => setStyleIntensity(parseFloat(e.target.value))}
                    className="slider"
                    disabled={isProcessing}
                  />
                  <div className="slider-labels" style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                    marginTop: '0.25rem'
                  }}>
                    <span>Subtle</span>
                    <span>Intense</span>
                  </div>
                </div>

                <div className="input-group">
                  <label className="input-label">Quality</label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value)}
                    className="input"
                    disabled={isProcessing}
                  >
                    <option value="fast">Fast (100 steps)</option>
                    <option value="standard">Standard (200 steps)</option>
                    <option value="high">High (300 steps)</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="control-section" style={{ marginTop: '1.5rem' }}>
                <h3 className="control-title">3. Generate</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleStyleTransfer(false)}
                    disabled={!contentImage || !styleImage || isProcessing}
                    style={{ width: '100%' }}
                  >
                    {isProcessing ? (
                      <>
                        <LoadingSpinner size="small" />
                        Processing...
                      </>
                    ) : (
                      '🎨 Apply Style Transfer'
                    )}
                  </button>
                  
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleStyleTransfer(true)}
                    disabled={!contentImage || !styleImage || isProcessing}
                    style={{ width: '100%' }}
                  >
                    ⚡ Quick Transfer
                  </button>

                  {(contentImage || styleImage || resultImage) && (
                    <button
                      className="btn btn-danger"
                      onClick={handleReset}
                      disabled={isProcessing}
                      style={{ width: '100%' }}
                    >
                      🔄 Reset All
                    </button>
                  )}
                </div>
              </div>

              {/* Style Mixer (Future Feature) */}
              <div className="control-section" style={{ marginTop: '1.5rem', opacity: 0.5 }}>
                <h3 className="control-title">🔮 Coming Soon</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  • Multi-style blending<br />
                  • Custom style training<br />
                  • Batch processing<br />
                  • Video style transfer
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p className="footer-text">
          Built with using React, Flask & PyTorch | Optimized for Apple Silicon M4
        </p>
      </footer>
    </div>
  );
}

export default App;