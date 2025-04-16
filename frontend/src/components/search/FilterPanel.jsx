
// src/components/search/FilterPanel.jsx
import React from 'react';
import PropTypes from 'prop-types';
import Dropdown from '../common/Dropdown';
import Button from '../common/Button';

const FilterPanel = ({ 
  filters, 
  availableFilters, 
  onFilterChange, 
  onReset,
  isDisabled 
}) => {
  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    onFilterChange(name, value);
  };
  
  // Check if any filters are active
  const hasActiveFilters = Object.values(filters).some(value => value !== '');
  
  return (
    <div className="filter-panel">
      <div className="filter-container">
        <Dropdown
          label="Phase"
          name="phase"
          value={filters.phase}
          onChange={handleFilterChange}
          options={availableFilters.phases}
          placeholder="Any Phase"
          disabled={isDisabled}
        />
        
        <Dropdown
          label="Gender"
          name="gender"
          value={filters.gender}
          onChange={handleFilterChange}
          options={[
            { value: 'ALL', label: 'All' },
            { value: 'MALE', label: 'Male' },
            { value: 'FEMALE', label: 'Female' }
          ]}
          placeholder="Any Gender"
          disabled={isDisabled}
        />
        
        <Dropdown
          label="Healthy Volunteers"
          name="healthyVolunteers"
          value={filters.healthyVolunteers}
          onChange={handleFilterChange}
          options={[
            { value: 'yes', label: 'Accepting' },
            { value: 'no', label: 'Not Accepting' }
          ]}
          placeholder="Any"
          disabled={isDisabled}
        />
        
        <Dropdown
          label="Status"
          name="status"
          value={filters.status}
          onChange={handleFilterChange}
          options={availableFilters.statuses}
          placeholder="Any Status"
          disabled={isDisabled}
        />
      </div>
      
      {hasActiveFilters && (
        <div className="filter-actions">
          <Button
            variant="text"
            size="small"
            onClick={onReset}
            disabled={isDisabled}
          >
            Reset Filters
          </Button>
        </div>
      )}
    </div>
  );
};

FilterPanel.propTypes = {
  filters: PropTypes.object.isRequired,
  availableFilters: PropTypes.object.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool.isRequired
};

export default FilterPanel;

