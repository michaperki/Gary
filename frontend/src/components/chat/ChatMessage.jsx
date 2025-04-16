// src/components/chat/ChatMessage.jsx
import React from 'react';
import PropTypes from 'prop-types';
import Evidence from './Evidence';

const ChatMessage = ({ message }) => {
  const { role, content, evidence, isError } = message;
  
  // Set classes based on message role
  const messageClasses = `message ${role} ${isError ? 'error' : ''}`;
  
  return (
    <div className={messageClasses}>
      <div className="message-header">
        <span className="message-role">
          {role === 'user' ? 'You' : 'Assistant'}
        </span>
      </div>
      
      <div className="message-content">
        {content}
      </div>
      
      {evidence && evidence.length > 0 && (
        <Evidence items={evidence} />
      )}
    </div>
  );
};

ChatMessage.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    evidence: PropTypes.array,
    isError: PropTypes.bool
  }).isRequired
};

export default ChatMessage;

