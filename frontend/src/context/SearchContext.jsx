// src/context/SearchContext.jsx - Context for managing search state and operations
import React, { createContext, useState, useContext, useCallback, useEffect } from 'react';
import { searchTrials, getFilterOptions } from '../api';
import ApiContext from './ApiContext';
import { logger } from '../utils/logger';

// Create context
export const SearchContext = createContext();

export const SearchProvider = ({ children }) => {
  // State for search
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [filters, setFilters] = useState({
    phase: '',
    gender: '',
    healthyVolunteers: '',
    status: ''
  });
  const [availableFilters, setAvailableFilters] = useState({
    phases: [],
    genders: ['ALL', 'MALE', 'FEMALE'],
    statuses: [],
    healthyVolunteers: ['yes', 'no']
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [hasMore, setHasMore] = useState(false);
  
  // Get API connection status from context
  const { isConnected } = useContext(ApiContext);

  // Load available filter options
  const loadFilterOptions = useCallback(async () => {
    if (!isConnected) return;
    
    try {
      logger.info('Loading filter options');
      const options = await getFilterOptions();
      setAvailableFilters(prev => ({
        ...prev,
        phases: options.phases || [],
        statuses: options.statuses || [],
        ...options
      }));
      logger.info('Filter options loaded');
    } catch (err) {
      logger.error('Error loading filter options:', err);
      setError('Failed to load filter options');
    }
  }, [isConnected]);

  // Load filter options on mount
  useEffect(() => {
    loadFilterOptions();
  }, [loadFilterOptions]);

  // Update a single filter
  const updateFilter = useCallback((name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset to page 1 when filters change
    setPage(1);
  }, []);

  // Reset all filters
  const resetFilters = useCallback(() => {
    setFilters({
      phase: '',
      gender: '',
      healthyVolunteers: '',
      status: ''
    });
    
    // Reset to page 1
    setPage(1);
  }, []);

  // Search trials
  const search = useCallback(async (searchQuery = null, page = 1, pageSize = 10) => {
    // If query is provided, update state
    if (searchQuery !== null) {
      setQuery(searchQuery);
    }
    
    // Use current query if not provided
    const finalQuery = searchQuery !== null ? searchQuery : query;
    
    if (!finalQuery.trim() || !isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      logger.info(`Searching trials: "${finalQuery}"`, { 
        filters, 
        page, 
        pageSize 
      });
      
      const data = await searchTrials(finalQuery, {
        ...filters,
        page,
        limit: pageSize
      });
      
      if (page === 1) {
        // New search, replace results
        setResults(data.results || []);
      } else {
        // Pagination, append results
        setResults(prev => [...prev, ...(data.results || [])]);
      }
      
      setTotalResults(data.total || 0);
      setHasMore((data.results || []).length >= pageSize);
      setPage(page);
      logger.info(`Search complete: ${data.results?.length || 0} results found`);
    } catch (err) {
      logger.error('Error searching trials:', err);
      setError('Failed to search for trials. Please try again.');
      setResults([]);
      setTotalResults(0);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, [query, filters, isConnected]);

  // Load more results (pagination)
  const loadMore = useCallback(() => {
    if (isLoading || !hasMore) return;
    
    const nextPage = page + 1;
    search(null, nextPage, pageSize);
  }, [isLoading, hasMore, page, pageSize, search]);

  // Context value
  const value = {
    query,
    results,
    totalResults,
    filters,
    availableFilters,
    isLoading,
    error,
    page,
    pageSize,
    hasMore,
    setQuery,
    search,
    updateFilter,
    resetFilters,
    loadMore,
    loadFilterOptions
  };

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
};

export default SearchContext;
