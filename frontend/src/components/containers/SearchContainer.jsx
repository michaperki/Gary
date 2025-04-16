// src/components/containers/SearchContainer.jsx
import React from 'react';
import SearchForm from '../search/SearchForm';
import SearchResults from '../search/SearchResults';
import useSearch from '../../hooks/useSearch';
import useApi from '../../hooks/useApi';

const SearchContainer = () => {
  // Get search functionality from hook
  const { 
    query,
    results, 
    totalResults,
    filters, 
    availableFilters,
    isLoading, 
    error,
    hasMore,
    search,
    updateFilter,
    resetFilters,
    loadMore
  } = useSearch();
  
  // Get API connection status
  const { isConnected } = useApi();
  
  // Handle search submission
  const handleSearch = (searchQuery) => {
    search(searchQuery);
  };
  
  // Handle filter changes
  const handleFilterChange = (name, value) => {
    updateFilter(name, value);
  };
  
  return (
    <div className="search-container">
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}
      
      <SearchForm
        onSearch={handleSearch}
        filters={filters}
        availableFilters={availableFilters}
        onFilterChange={handleFilterChange}
        onResetFilters={resetFilters}
        isLoading={isLoading}
        isDisabled={!isConnected}
      />
      
      <SearchResults
        results={results}
        totalResults={totalResults}
        isLoading={isLoading}
        hasMore={hasMore}
        onLoadMore={loadMore}
        query={query}
      />
    </div>
  );
};

export default SearchContainer;
