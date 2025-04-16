// src/api/index.js - Centralized exports for API functionality
import apiClient from './apiClient';
import ENDPOINTS from './endpoints';

// Import and re-export all services
import { checkApiHealth } from './services/healthService';
import { 
  sendChatMessage, 
  getConversation,
  getConversations 
} from './services/chatService';
import { 
  searchTrials, 
  getFilterOptions,
  getTrialById 
} from './services/trialService';

// Export everything in a clean, organized way
export {
  // Base API client for custom requests
  apiClient,
  
  // Endpoints for direct access if needed
  ENDPOINTS,
  
  // Health service exports
  checkApiHealth,
  
  // Chat service exports
  sendChatMessage,
  getConversation,
  getConversations,
  
  // Trial service exports
  searchTrials,
  getFilterOptions,
  getTrialById
};

// Default export the entire API object
export default {
  client: apiClient,
  endpoints: ENDPOINTS,
  health: {
    checkApiHealth
  },
  chat: {
    sendMessage: sendChatMessage,
    getConversation,
    getConversations
  },
  trials: {
    search: searchTrials,
    getFilterOptions,
    getById: getTrialById
  }
};
