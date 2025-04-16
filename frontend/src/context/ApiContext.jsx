// src/context/ApiContext.jsx - Context for API health and status with fixed health check
import React, { createContext, useState, useEffect, useCallback, useRef } from 'react';
import { checkApiHealth } from '../api';
import { logger } from '../utils/logger';

// Create context
export const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  // State for API connection status
  const [isConnected, setIsConnected] = useState(true);
  const [lastChecked, setLastChecked] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState(null);
  
  // Use a ref to track if a health check is already in progress
  const healthCheckInProgress = useRef(false);
  
  // Use a ref to track the health check interval
  const healthCheckIntervalRef = useRef(null);

  // Function to check API health
  const checkConnection = useCallback(async (force = false) => {
    // Prevent concurrent health checks
    if (healthCheckInProgress.current && !force) {
      logger.debug('Health check already in progress, skipping...');
      return;
    }
    
    // Set the flag to indicate a check is in progress
    healthCheckInProgress.current = true;
    setIsChecking(true);
    setError(null);
    
    try {
      logger.info('Checking API connection...');
      const health = await checkApiHealth();
      const isHealthy = health && health.status === 'ok';
      
      setIsConnected(isHealthy);
      setLastChecked(new Date());
      
      logger.info(`API connection: ${isHealthy ? 'Connected' : 'Disconnected'}`);
      
      return isHealthy;
    } catch (err) {
      logger.error('API connection check failed:', err);
      setIsConnected(false);
      setError(err.message || 'Unable to connect to API');
      return false;
    } finally {
      // Reset the flag to allow future checks
      healthCheckInProgress.current = false;
      setIsChecking(false);
    }
  }, []);

  // Initial connection check on mount
  useEffect(() => {
    // Initial check when component mounts
    checkConnection();
    
    // Set up event listeners for API errors
    const handleNetworkError = () => {
      logger.error('Network error detected');
      setIsConnected(false);
    };
    
    const handleServerError = (event) => {
      logger.error(`Server error detected: ${event.detail?.status || 'Unknown'}`);
      setIsConnected(false);
    };
    
    // Add event listeners
    window.addEventListener('api:network-error', handleNetworkError);
    window.addEventListener('api:server-error', handleServerError);
    
    // Set up periodic health check (every 5 minutes instead of 2 minutes)
    // Using a ref to store the interval ID for proper cleanup
    healthCheckIntervalRef.current = setInterval(() => {
      checkConnection();
    }, 5 * 60 * 1000); // 5 minutes
    
    // Clean up
    return () => {
      window.removeEventListener('api:network-error', handleNetworkError);
      window.removeEventListener('api:server-error', handleServerError);
      
      // Clear the interval using the ref
      if (healthCheckIntervalRef.current) {
        clearInterval(healthCheckIntervalRef.current);
      }
    };
  }, [checkConnection]);

  // Manual health check function exposed to consumers
  const checkHealth = useCallback(() => {
    return checkConnection(true); // Pass force=true to bypass the in-progress check
  }, [checkConnection]);

  // Context value
  const value = {
    isConnected,
    lastChecked,
    isChecking,
    error,
    checkHealth // Expose the manual check function
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
};

export default ApiContext;
