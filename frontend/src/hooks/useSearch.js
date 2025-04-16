
// src/hooks/useSearch.js - Custom hook for search functionality
import { useContext } from 'react';
import SearchContext from '../context/SearchContext';

export const useSearch = () => {
  // Get search context
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  
  return context;
};

export default useSearch;

