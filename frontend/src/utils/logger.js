// src/utils/logger.js - Enhanced logging utility
const LOG_LEVEL = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

// Get log level from environment or default to INFO in production, DEBUG in development
const CURRENT_LOG_LEVEL = process.env.REACT_APP_LOG_LEVEL ? 
  LOG_LEVEL[process.env.REACT_APP_LOG_LEVEL] : 
  (process.env.NODE_ENV === 'production' ? LOG_LEVEL.INFO : LOG_LEVEL.DEBUG);

export const logger = {
  debug: (message, data) => {
    if (CURRENT_LOG_LEVEL <= LOG_LEVEL.DEBUG) {
      console.debug(`[DEBUG] ${message}`, data || '');
    }
  },
  
  info: (message, data) => {
    if (CURRENT_LOG_LEVEL <= LOG_LEVEL.INFO) {
      console.info(`[INFO] ${message}`, data || '');
    }
  },
  
  warn: (message, data) => {
    if (CURRENT_LOG_LEVEL <= LOG_LEVEL.WARN) {
      console.warn(`[WARN] ${message}`, data || '');
    }
  },
  
  error: (message, data) => {
    if (CURRENT_LOG_LEVEL <= LOG_LEVEL.ERROR) {
      console.error(`[ERROR] ${message}`, data || '');
    }
  },
  
  // Allow grouping related logs together
  group: (name, logFunction) => {
    if (CURRENT_LOG_LEVEL <= LOG_LEVEL.DEBUG) {
      console.group(name);
      logFunction();
      console.groupEnd();
    }
  }
};

