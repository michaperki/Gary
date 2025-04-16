// src/components/layout/TabNavigation.jsx - Enhanced tab navigation
import React from 'react';
import PropTypes from 'prop-types';

const TABS = [
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'search', label: 'Search Trials', icon: '🔍' }
];

const TabNavigation = ({ activeTab, onTabChange }) => {
  return (
    <nav className="tabs" role="tablist" aria-label="Application sections">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          className={`tab ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`${tab.id}-panel`}
          id={`${tab.id}-tab`}
        >
          <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
          <span className="tab-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
};

TabNavigation.propTypes = {
  activeTab: PropTypes.string.isRequired,
  onTabChange: PropTypes.func.isRequired
};

export default TabNavigation;
