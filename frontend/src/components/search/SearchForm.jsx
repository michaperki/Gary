// src/components/search/SearchForm.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Button from '../common/Button';
import Input from '../common/Input';
import FilterPanel from './FilterPanel';

const SearchForm = ({ 
  onSearch, 
  filters, 
  availableFilters,
  onFilterChange, 
  onResetFilters,
  isLoading, 
  isDisabled 
}) => {
  const [query, setQuery] = useState('');
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!query.trim() || isLoading || isDisabled) return;
    
    onSearch(query);
  };
  
  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="search-input-container">
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for clinical trials..."
          disabled={isLoading || isDisabled}
          className="search-input"
        />
        
        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
          isDisabled={isDisabled || !query.trim()}
        >
          Search
        </Button>
      </div>
      
      <FilterPanel
        filters={filters}
        availableFilters={availableFilters}
        onFilterChange={onFilterChange}
        onReset={onResetFilters}
        isDisabled={isDisabled}
      />
    </form>
  );
};

SearchForm.propTypes = {
  onSearch: PropTypes.func.isRequired,
  filters: PropTypes.object.isRequired,
  availableFilters: PropTypes.object.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onResetFilters: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isDisabled: PropTypes.bool.isRequired
};

export default SearchForm;

