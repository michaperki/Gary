// src/components/layout/Header.jsx - Enhanced version with logo and better layout
import React from 'react';
import PropTypes from 'prop-types';
import TabNavigation from './TabNavigation';
import Button from '../common/Button';
import useApi from '../../hooks/useApi';
import { formatDate } from '../../utils/formatter';

// Logo could be imported from assets folder
// import Logo from '../../assets/logo.svg';

const Header = ({ 
  activeTab, 
  onTabChange
}) => {
  // Get API status from context
  const { isConnected, lastChecked, isChecking, checkHealth } = useApi();
  
  // Format last checked time if available
  const formattedLastChecked = lastChecked 
    ? formatDate(lastChecked) + ' at ' + lastChecked.toLocaleTimeString()
    : 'Not checked yet';
  
  // Handle manual refresh click
  const handleRefreshClick = () => {
    if (!isChecking) {
      checkHealth();
    }
  };
  
  return (
    <header className="app-header">
      <div className="header-content">
        <h1 className="app-title">
          {/* {Logo && <img src={Logo} alt="Logo" className="app-logo" />} */}
          <span>Clinical Trials AI Assistant</span>
        </h1>
        
        <div className="api-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'API Connected' : 'API Disconnected'}
          </span>
          
          <span className="last-checked">
            Last checked: {formattedLastChecked}
          </span>
          
          <Button
            variant="text"
            size="small"
            onClick={handleRefreshClick}
            isLoading={isChecking}
            className="refresh-button"
          >
            {isChecking ? 'Checking...' : 'Check Now'}
          </Button>
        </div>
        
        {/* User section - can be used for future auth implementation */}
        {/* <div className="user-section">
          <div className="user-avatar">
            U
          </div>
          <span className="user-name">User</span>
          <button className="user-menu-button">
            ⌄
          </button>
        </div> */}
        
        {!isConnected && (
          <div className="api-warning">
            Cannot connect to API server. Please check your backend connection.
          </div>
        )}
      </div>
      
      <TabNavigation 
        activeTab={activeTab} 
        onTabChange={onTabChange} 
      />
    </header>
  );
};

Header.propTypes = {
  activeTab: PropTypes.string.isRequired,
  onTabChange: PropTypes.func.isRequired
};

export default Header;
