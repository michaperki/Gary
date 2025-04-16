
// src/components/common/Dropdown.jsx
import React from 'react';
import PropTypes from 'prop-types';

const Dropdown = ({
  value,
  onChange,
  options = [],
  placeholder = 'Select an option',
  name,
  id,
  label,
  error,
  disabled = false,
  className = '',
  ...props
}) => {
  // Generate unique id if not provided
  const selectId = id || `dropdown-${name || Math.random().toString(36).substr(2, 9)}`;
  
  // Handle change event
  const handleChange = (e) => {
    onChange(e);
  };
  
  return (
    <div className="dropdown-wrapper mb-4">
      {label && (
        <label 
          htmlFor={selectId} 
          className="block text-sm font-medium mb-1"
        >
          {label}
        </label>
      )}
      
      <select
        id={selectId}
        name={name}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className={`w-full px-4 py-2 border rounded appearance-none bg-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${error ? 'border-red-500' : 'border-gray-300'} ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''} ${className}`}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((option, index) => (
          <option 
            key={index} 
            value={typeof option === 'object' ? option.value : option}
          >
            {typeof option === 'object' ? option.label : option}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};

Dropdown.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        value: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired
      })
    ])
  ),
  placeholder: PropTypes.string,
  name: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

export default Dropdown;

