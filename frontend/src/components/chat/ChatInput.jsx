
// src/components/chat/ChatInput.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Button from '../common/Button';

const ChatInput = ({ 
  onSendMessage, 
  onNewChat, 
  isLoading, 
  isDisabled,
  hasMessages 
}) => {
  const [message, setMessage] = useState('');
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading || isDisabled) return;
    
    onSendMessage(message);
    setMessage('');
  };
  
  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask about clinical trials..."
        disabled={isLoading || isDisabled}
        className="chat-input-field"
      />
      
      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading}
        isDisabled={isDisabled || !message.trim()}
      >
        Send
      </Button>
      
      <Button
        type="button"
        variant="secondary"
        onClick={onNewChat}
        isDisabled={!hasMessages || isLoading}
        className="new-chat-btn"
      >
        New Chat
      </Button>
    </form>
  );
};

ChatInput.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  onNewChat: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isDisabled: PropTypes.bool.isRequired,
  hasMessages: PropTypes.bool.isRequired
};

export default ChatInput;
