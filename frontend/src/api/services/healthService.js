// src/api/services/healthService.js - Enhanced health check service with caching
import apiClient from '../apiClient';
import ENDPOINTS from '../endpoints';
import { logger } from '../../utils/logger';

// Cache for health check results
let healthCache = {
  status: null,
  timestamp: null,
  expiresIn: 30000 // 30 seconds cache expiry
};

/**
 * Check API health with caching to prevent excessive requests
 * @returns {Promise<Object>} Health check result
 */
export const checkApiHealth = async () => {
  const now = Date.now();
  
  // If we have a cached result that's still valid, return it
  if (
    healthCache.status && 
    healthCache.timestamp && 
    (now - healthCache.timestamp) < healthCache.expiresIn
  ) {
    logger.debug('Using cached health check result', {
      age: now - healthCache.timestamp,
      status: healthCache.status
    });
    return { status: healthCache.status };
  }
  
  try {
    logger.info('Performing API health check');
    const response = await apiClient.get(ENDPOINTS.HEALTH);
    
    // Cache the result
    healthCache = {
      status: response.data.status,
      timestamp: now,
      expiresIn: 30000
    };
    
    return response.data;
  } catch (error) {
    logger.error('API health check failed:', error);
    
    // Cache the failure too to prevent retry storms
    healthCache = {
      status: 'error',
      timestamp: now,
      expiresIn: 15000 // Shorter cache time for errors
    };
    
    throw error;
  }
};

/**
 * Force a fresh health check by bypassing the cache
 * @returns {Promise<Object>} Health check result
 */
export const forceFreshHealthCheck = async () => {
  try {
    logger.info('Forcing fresh API health check');
    const response = await apiClient.get(ENDPOINTS.HEALTH);
    
    // Update cache with fresh result
    healthCache = {
      status: response.data.status,
      timestamp: Date.now(),
      expiresIn: 30000
    };
    
    return response.data;
  } catch (error) {
    logger.error('Forced API health check failed:', error);
    throw error;
  }
};

/**
 * Clear the health check cache
 */
export const clearHealthCache = () => {
  healthCache = {
    status: null,
    timestamp: null,
    expiresIn: 30000
  };
  logger.debug('Health check cache cleared');
};
