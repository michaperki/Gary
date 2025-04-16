// src/api/apiClient.js - Enhanced Axios client instance with improved configuration
import axios from 'axios';
import { logger } from '../utils/logger';

// API base URL - read from environment variable or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout
});

// Add request interceptor for logging and authentication
apiClient.interceptors.request.use(
  (config) => {
    logger.info(`API Request: ${config.method.toUpperCase()} ${config.url}`, { url: config.url, method: config.method });
    
    // Get authentication token from localStorage if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Ensure OPTIONS requests have the right headers for CORS preflight
    if (config.method.toLowerCase() === 'options') {
      config.headers['Access-Control-Request-Method'] = 'POST';
      config.headers['Access-Control-Request-Headers'] = 'Content-Type, Authorization';
    }
    
    return config;
  },
  (error) => {
    logger.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and response processing
apiClient.interceptors.response.use(
  (response) => {
    // Log successful responses if needed
    logger.debug('API Response:', { 
      url: response.config.url, 
      status: response.status, 
      data: response.data 
    });
    
    return response;
  },
  (error) => {
    // Enhanced error handling
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      logger.error('API Error Response:', { 
        url: error.config?.url,
        status: error.response.status, 
        data: error.response.data,
        headers: error.response.headers
      });
      
      // Handle authentication errors
      if (error.response.status === 401) {
        // Dispatch event for unauthorized access
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
      
      // Handle server errors
      if (error.response.status >= 500) {
        window.dispatchEvent(new CustomEvent('api:server-error', { 
          detail: { status: error.response.status }
        }));
      }
      
    } else if (error.request) {
      // The request was made but no response was received
      logger.error('API No Response:', { 
        url: error.config?.url,
        request: error.request
      });
      
      // Dispatch network error event
      window.dispatchEvent(new CustomEvent('api:network-error'));
      
    } else {
      // Something happened in setting up the request that triggered an Error
      logger.error('API Setup Error:', { 
        message: error.message,
        config: error.config
      });
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
