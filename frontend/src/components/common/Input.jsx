
// src/components/common/Input.jsx
import React from 'react';
import PropTypes from 'prop-types';

const Input = ({
  type = 'text',
  value,
  onChange,
  placeholder = '',
  name,
  id,
  label,
  error,
  disabled = false,
  className = '',
  ...props
}) => {
  // Generate unique id if not provided
  const inputId = id || `input-${name || Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="input-wrapper mb-4">
      {label && (
        <label 
          htmlFor={inputId} 
          className="block text-sm font-medium mb-1"
        >
          {label}
        </label>
      )}
      
      <input
        id={inputId}
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${error ? 'border-red-500' : 'border-gray-300'} ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'} ${className}`}
        {...props}
      />
      
      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};

Input.propTypes = {
  type: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  name: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

export default Input;

