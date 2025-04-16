// src/App.jsx - Main application component with context providers
import React, { useState } from 'react';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import ChatContainer from './components/containers/ChatContainer';
import SearchContainer from './components/containers/SearchContainer';

// Context providers
import { ApiProvider } from './context/ApiContext';
import { ChatProvider } from './context/ChatContext';
import { SearchProvider } from './context/SearchContext';

// Import styles
import './styles/global.css';
import './styles/utils.css';
import './styles/components/chat.css';
import './styles/components/search.css';
import './styles/components/header.css';
import './styles/components/tabs.css'; // Import the new tabs CSS

// Application version
const APP_VERSION = '1.0.0';

function App() {
  // State for active tab
  const [activeTab, setActiveTab] = useState('chat');
  
  // Handle tab change
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };
  
  return (
    <ApiProvider>
      <div className="app">
        <Header 
          activeTab={activeTab} 
          onTabChange={handleTabChange}
        />
        
        <main className="app-main" aria-live="polite">
          <div 
            id="chat-panel" 
            role="tabpanel" 
            aria-labelledby="chat-tab"
            className={activeTab === 'chat' ? 'active-panel' : 'hidden-panel'}
          >
            {activeTab === 'chat' && (
              <ChatProvider>
                <ChatContainer />
              </ChatProvider>
            )}
          </div>
          
          <div 
            id="search-panel" 
            role="tabpanel" 
            aria-labelledby="search-tab"
            className={activeTab === 'search' ? 'active-panel' : 'hidden-panel'}
          >
            {activeTab === 'search' && (
              <SearchProvider>
                <SearchContainer />
              </SearchProvider>
            )}
          </div>
        </main>
        
        <Footer version={APP_VERSION} />
      </div>
    </ApiProvider>
  );
}

export default App;
