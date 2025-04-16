
// src/hooks/useApi.js - Custom hook for API status
import { useContext } from 'react';
import ApiContext from '../context/ApiContext';

export const useApi = () => {
  // Get API context
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  
  return context;
};

export default useApi;
