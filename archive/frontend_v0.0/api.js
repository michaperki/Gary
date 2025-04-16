// src/api.js - Centralized API service with improved error handling
import axios from 'axios';

// API base URL - read from environment variable or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout
  // Add withCredentials if using cookies for authentication
  // withCredentials: true
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    
    // Ensure OPTIONS requests have the right headers for CORS preflight
    if (config.method.toLowerCase() === 'options') {
      config.headers['Access-Control-Request-Method'] = 'POST';
      config.headers['Access-Control-Request-Headers'] = 'Content-Type';
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log errors
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', `Status: ${error.response.status}`, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      // Could be CORS issues or server not running
      console.error('API Error: No response received', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error:', error.message);
    }
    
    // You can handle specific error status codes here
    if (error.response && error.response.status === 401) {
      // Handle unauthorized access
      console.log('Unauthorized access. Redirecting to login...');
    }
    
    return Promise.reject(error);
  }
);

// API function for searching clinical trials
export const searchTrials = async (query, filters = {}) => {
  const params = new URLSearchParams({ q: query });
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  
  try {
    const response = await api.get(`/trials/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error searching trials:', error);
    throw error;
  }
};

// API function for sending chat messages
export const sendChatMessage = async (message, conversationId = null, userId = 'user123') => {
  try {
    const response = await api.post('/chat', {
      message,
      conversation_id: conversationId,
      user_id: userId
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// API function for loading conversation history
export const getConversation = async (conversationId) => {
  try {
    const response = await api.get(`/conversations/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error('Error loading conversation:', error);
    throw error;
  }
};

// API function for getting available filter options
export const getFilterOptions = async () => {
  try {
    const response = await api.get('/trials/filters');
    return response.data;
  } catch (error) {
    console.error('Error fetching filter options:', error);
    throw error;
  }
};

// API function for health check
export const checkApiHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
};

// Export the axios instance for custom API calls
export default api;

