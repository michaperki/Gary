
// src/components/search/SearchResults.jsx
import React from 'react';
import PropTypes from 'prop-types';
import TrialCard from './TrialCard';
import Loading from '../common/Loading';
import Button from '../common/Button';

const SearchResults = ({ 
  results, 
  totalResults,
  isLoading, 
  hasMore,
  onLoadMore,
  query
}) => {
  // If loading with no results, show loading indicator
  if (isLoading && results.length === 0) {
    return (
      <div className="search-results">
        <div className="loading-container">
          <Loading />
        </div>
      </div>
    );
  }
  
  // If no results and query was entered, show no results message
  if (results.length === 0 && query) {
    return (
      <div className="search-results">
        <div className="no-results">
          <p>No clinical trials found matching your criteria.</p>
        </div>
      </div>
    );
  }
  
  // If no query entered, show empty state
  if (results.length === 0 && !query) {
    return (
      <div className="search-results">
        <div className="empty-results">
          <p>Enter search terms above to find clinical trials.</p>
        </div>
      </div>
    );
  }
  
  // Show results
  return (
    <div className="search-results">
      <h3 className="results-count">
        {totalResults} Clinical Trials Found
      </h3>
      
      {results.map((trial, index) => (
        <TrialCard key={index} trial={trial} />
      ))}
      
      {hasMore && (
        <div className="load-more-container">
          <Button
            variant="secondary"
            onClick={onLoadMore}
            isLoading={isLoading}
          >
            Load More Results
          </Button>
        </div>
      )}
    </div>
  );
};

SearchResults.propTypes = {
  results: PropTypes.array.isRequired,
  totalResults: PropTypes.number.isRequired,
  isLoading: PropTypes.bool.isRequired,
  hasMore: PropTypes.bool.isRequired,
  onLoadMore: PropTypes.func.isRequired,
  query: PropTypes.string
};

export default SearchResults;
