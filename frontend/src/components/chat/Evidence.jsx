
// src/components/chat/Evidence.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Button from '../common/Button';

const Evidence = ({ items }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Show only first 3 items when collapsed
  const visibleItems = isExpanded ? items : items.slice(0, 3);
  const hasMore = items.length > 3;
  
  return (
    <div className="evidence">
      <h4 className="evidence-title">
        Referenced Trials:
      </h4>
      
      <ul className="evidence-list">
        {visibleItems.map((item, index) => (
          <li key={index} className="evidence-item">
            <a 
              href={item.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="evidence-link"
            >
              {item.title} {item.nct_id && `(NCT ID: ${item.nct_id})`}
            </a>
          </li>
        ))}
      </ul>
      
      {hasMore && (
        <Button
          variant="text"
          size="small"
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2"
        >
          {isExpanded ? 'Show Less' : `Show ${items.length - 3} More`}
        </Button>
      )}
    </div>
  );
};

Evidence.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string.isRequired,
      source_url: PropTypes.string.isRequired,
      nct_id: PropTypes.string
    })
  ).isRequired
};

export default Evidence;

