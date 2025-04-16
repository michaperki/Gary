
// src/components/common/Loading.jsx
import React from 'react';
import PropTypes from 'prop-types';

const Loading = ({ 
  size = 'medium', 
  text = 'Loading...', 
  showText = true,
  className = '' 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
  
  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`loading-spinner ${sizeClasses[size]}`}>
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
      
      {showText && (
        <p className="mt-2 text-gray-600">
          {text}
        </p>
      )}
    </div>
  );
};

Loading.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  text: PropTypes.string,
  showText: PropTypes.bool,
  className: PropTypes.string
};

export default Loading;
