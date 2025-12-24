import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload, FaImage, FaCheckCircle } from 'react-icons/fa';
import './ImageUploader.css';

const ImageUploader = ({ label, onUpload, currentImage, disabled }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    multiple: false,
    disabled
  });

  return (
    <div className="image-uploader">
      <label className="uploader-label">{label}</label>
      
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''} ${currentImage ? 'has-image' : ''} ${disabled ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        
        {currentImage ? (
          <div className="preview-container">
            <img 
              src={currentImage.preview} 
              alt="Preview" 
              className="preview-image"
            />
            <div className="preview-overlay">
              <FaCheckCircle className="check-icon" />
              <p className="preview-text">Image uploaded</p>
              <p className="preview-hint">Click or drag to replace</p>
            </div>
          </div>
        ) : (
          <div className="upload-prompt">
            <FaUpload className="upload-icon" />
            <p className="upload-text">
              {isDragActive ? 'Drop image here' : 'Drag & drop or click to upload'}
            </p>
            <p className="upload-hint">PNG, JPG up to 16MB</p>
          </div>
        )}
      </div>

      {currentImage && (
        <div className="image-info">
          <FaImage /> {currentImage.filename}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;