import axios from 'axios';

// Base URL for API requests
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for long processing
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for debugging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const api = {
  /**
   * Health check endpoint
   */
  checkHealth: () => {
    return apiClient.get('/health');
  },

  /**
   * Upload an image file
   * @param {File} file - Image file to upload
   */
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Get available style presets
   */
  getStyles: () => {
    return apiClient.get('/api/styles');
  },

  /**
   * Perform style transfer
   * @param {Object} data - Transfer parameters
   * @param {string} data.content_image - Path to content image
   * @param {string} data.style_image - Path to style image
   * @param {number} data.intensity - Style intensity (0.1 - 2.0)
   * @param {string} data.quality - Quality setting ('fast', 'standard', 'high')
   */
  styleTransfer: (data) => {
    return apiClient.post('/api/transfer', data, {
      timeout: 600000, // 10 minutes for high quality
    });
  },

  /**
   * Perform quick style transfer (fewer iterations)
   * @param {Object} data - Transfer parameters
   * @param {string} data.content_image - Path to content image
   * @param {string} data.style_image - Path to style image
   * @param {number} data.intensity - Style intensity (0.1 - 2.0)
   */
  quickTransfer: (data) => {
    return apiClient.post('/api/quick-transfer', data, {
      timeout: 300000, // 5 minutes
    });
  },

  /**
   * Generate variations of an image
   * @param {Object} data - Generation parameters
   * @param {string} data.image - Path to source image
   * @param {number} data.num_variations - Number of variations to generate
   */
  generateVariations: (data) => {
    return apiClient.post('/api/variations', data);
  },

  /**
   * Get gallery of saved images
   */
  getGallery: () => {
    return apiClient.get('/api/gallery');
  },

  /**
   * Delete an image from gallery
   * @param {string} filename - Name of file to delete
   */
  deleteFromGallery: (filename) => {
    return apiClient.delete(`/api/gallery/${filename}`);
  },

  /**
   * Clean up old images from gallery
   * @param {number} maxAgeHours - Maximum age of files in hours
   */
  cleanupGallery: (maxAgeHours = 24) => {
    return apiClient.post('/api/gallery/cleanup', {
      max_age_hours: maxAgeHours,
    });
  },

  /**
   * Get gallery statistics
   */
  getGalleryInfo: () => {
    return apiClient.get('/api/gallery/info');
  },

  /**
   * Get full URL for an image
   * @param {string} filename - Image filename
   */
  getImageUrl: (filename) => {
    return `${API_BASE_URL}/api/image/${filename}`;
  },

  /**
   * Download an image
   * @param {string} filename - Image filename
   */
  downloadImage: async (filename) => {
    try {
      const response = await apiClient.get(`/api/image/${filename}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading image:', error);
      throw error;
    }
  },
};

export default api;