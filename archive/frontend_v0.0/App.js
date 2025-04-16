// App.js - Main application component with API service integration
import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { 
  searchTrials, 
  sendChatMessage, 
  getFilterOptions, 
  getConversation, 
  checkApiHealth 
} from './api';

function App() {
  // State for chat
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  // State for search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [filters, setFilters] = useState({
    phase: '',
    gender: '',
    healthyVolunteers: ''
  });
  const [availableFilters, setAvailableFilters] = useState({
    phases: []
  });
  
  // UI state
  const [activeTab, setActiveTab] = useState('chat');
  const [apiConnected, setApiConnected] = useState(true);
  
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Check API health and load filter options on component mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check if API is available
        const health = await checkApiHealth();
        setApiConnected(health.status === 'ok');
        
        // Load available filters
        const filters = await getFilterOptions();
        setAvailableFilters(filters);
      } catch (error) {
        console.error('Error initializing app:', error);
        setApiConnected(false);
      }
    };
    
    initializeApp();
  }, []);

  // Scroll to bottom when conversation updates
  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Handle sending chat messages
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    // Add user message to conversation
    const userMessage = {
      role: 'user',
      content: message
    };
    
    // Store the message text before clearing the input
    const messageText = message;
    
    setConversation(prev => [...prev, userMessage]);
    setLoading(true);
    setMessage('');
    
    try {
      // Use the API service to send the message
      const response = await sendChatMessage(messageText, conversationId);
      
      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
      
      // Add assistant response to conversation
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        evidence: response.evidence
      };
      
      setConversation(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message to conversation
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.'
      };
      
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Handle searching for trials
  const handleSearchTrials = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    
    try {
      // Use the API service to search trials
      const data = await searchTrials(searchQuery, {
        phase: filters.phase,
        gender: filters.gender,
        healthy_volunteers: filters.healthyVolunteers
      });
      
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Error searching trials:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Start a new conversation
  const startNewConversation = () => {
    setConversation([]);
    setConversationId(null);
  };

  // Load existing conversation
  const loadConversation = async (id) => {
    if (!id) return;
    
    setLoading(true);
    
    try {
      const data = await getConversation(id);
      setConversation(data.messages || []);
      setConversationId(data.conversation_id);
    } catch (error) {
      console.error('Error loading conversation:', error);
      // Handle error (e.g., show notification)
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Clinical Trials AI Assistant</h1>
        {!apiConnected && (
          <div className="api-warning">
            ⚠️ Cannot connect to API server. Please check your backend connection.
          </div>
        )}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            Search Trials
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'chat' ? (
          <div className="chat-container">
            <div className="chat-messages">
              {conversation.length === 0 ? (
                <div className="welcome-message">
                  <h2>Welcome to the Clinical Trials AI Assistant</h2>
                  <p>Ask me questions about clinical trials and I'll help you find relevant information for your patients.</p>
                  <div className="sample-questions">
                    <p>Examples:</p>
                    <ul>
                      <li>"What clinical trials are available for melanoma patients who failed immunotherapy?"</li>
                      <li>"Are there any phase 2 trials for EGFR-positive lung cancer patients?"</li>
                      <li>"Tell me about trials accepting healthy volunteers for vaccine studies"</li>
                    </ul>
                  </div>
                </div>
              ) : (
                conversation.map((msg, index) => (
                  <div key={index} className={`message ${msg.role}`}>
                    <div className="message-content">
                      {msg.content}
                    </div>
                    {msg.evidence && (
                      <div className="evidence">
                        <h4>Referenced Trials:</h4>
                        <ul>
                          {msg.evidence.map((evidence, idx) => (
                            <li key={idx}>
                              <a href={evidence.source_url} target="_blank" rel="noopener noreferrer">
                                {evidence.title} (NCT ID: {evidence.nct_id})
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))
              )}
              {loading && (
                <div className="message assistant loading">
                  <div className="loading-indicator">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about clinical trials..."
                disabled={loading || !apiConnected}
              />
              <button type="submit" disabled={loading || !message.trim() || !apiConnected}>
                Send
              </button>
              <button 
                type="button" 
                className="new-chat-btn"
                onClick={startNewConversation}
                disabled={conversation.length === 0}
              >
                New Chat
              </button>
            </form>
          </div>
        ) : (
          <div className="search-container">
            <form className="search-form" onSubmit={handleSearchTrials}>
              <div className="search-input-container">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for clinical trials..."
                  className="search-input"
                  disabled={loading || !apiConnected}
                />
                <button type="submit" disabled={loading || !searchQuery.trim() || !apiConnected}>
                  Search
                </button>
              </div>
              
              <div className="filter-container">
                <div className="filter">
                  <label htmlFor="phase">Phase:</label>
                  <select 
                    id="phase" 
                    name="phase" 
                    value={filters.phase}
                    onChange={handleFilterChange}
                    disabled={!apiConnected}
                  >
                    <option value="">Any Phase</option>
                    {availableFilters.phases.map((phase, index) => (
                      <option key={index} value={phase}>{phase}</option>
                    ))}
                  </select>
                </div>
                
                <div className="filter">
                  <label htmlFor="gender">Gender:</label>
                  <select 
                    id="gender" 
                    name="gender" 
                    value={filters.gender}
                    onChange={handleFilterChange}
                    disabled={!apiConnected}
                  >
                    <option value="">Any Gender</option>
                    <option value="ALL">All</option>
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                  </select>
                </div>
                
                <div className="filter">
                  <label htmlFor="healthyVolunteers">Healthy Volunteers:</label>
                  <select 
                    id="healthyVolunteers" 
                    name="healthyVolunteers" 
                    value={filters.healthyVolunteers}
                    onChange={handleFilterChange}
                    disabled={!apiConnected}
                  >
                    <option value="">Any</option>
                    <option value="yes">Accepting</option>
                    <option value="no">Not Accepting</option>
                  </select>
                </div>
              </div>
            </form>

            <div className="search-results">
              {loading ? (
                <div className="loading-container">
                  <div className="loading-indicator">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              ) : searchResults.length > 0 ? (
                <>
                  <h3>{searchResults.length} Clinical Trials Found</h3>
                  {searchResults.map((trial, index) => (
                    <div key={index} className="trial-card">
                      <h3>{trial.title}</h3>
                      <div className="trial-details">
                        <p><strong>NCT ID:</strong> {trial.nct_id}</p>
                        <p><strong>Principal Investigator:</strong> {trial.principal_investigator}</p>
                        <p><strong>Phase:</strong> {trial.phase}</p>
                        <p><strong>Eligibility:</strong> {trial.gender} • {trial.age_range}</p>
                        <p><strong>Healthy Volunteers:</strong> {trial.healthy_volunteers === 'yes' ? 'Accepted' : 'Not Accepted'}</p>
                        <p><strong>Conditions:</strong> {trial.conditions}</p>
                        <p><strong>Interventions:</strong> {trial.interventions}</p>
                      </div>
                      <div className="trial-actions">
                        <a 
                          href={trial.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="view-details-btn"
                        >
                          View on ClinicalTrials.gov
                        </a>
                      </div>
                    </div>
                  ))}
                </>
              ) : searchQuery && !loading ? (
                <div className="no-results">
                  <p>No clinical trials found matching your criteria.</p>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Clinical Trials AI Assistant • Powered by Vector Search and LLM Technology</p>
      </footer>
    </div>
  );
}

export default App;
