// src/api/endpoints.js - Centralized API endpoint definitions
// This helps maintain consistency and makes it easier to update endpoints when needed

const ENDPOINTS = {
  // Health/system endpoints
  HEALTH: '/health',
  
  // Chat endpoints
  CHAT: '/chat',
  CONVERSATIONS: '/conversations',
  CONVERSATION_BY_ID: (id) => `/conversations/${id}`,
  
  // Trial endpoints
  TRIALS_SEARCH: '/trials/search',
  TRIALS_FILTERS: '/trials/filters',
  TRIAL_BY_ID: (id) => `/trials/${id}`,
  
  // User endpoints (for future expansion)
  USER_PROFILE: '/user/profile',
  USER_SETTINGS: '/user/settings',
};

export default ENDPOINTS;
