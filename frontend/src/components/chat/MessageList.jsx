
// src/components/chat/MessageList.jsx
import React from 'react';
import PropTypes from 'prop-types';
import ChatMessage from './ChatMessage';
import Loading from '../common/Loading';
import WelcomeMessage from './WelcomeMessage';

const MessageList = ({ 
  messages, 
  isLoading, 
  messagesEndRef,
  onSampleQuestionClick
}) => {
  return (
    <div className="chat-messages">
      {messages.length === 0 ? (
        <WelcomeMessage onSampleQuestionClick={onSampleQuestionClick} />
      ) : (
        <>
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </>
      )}
      
      {isLoading && (
        <div className="message assistant loading">
          <Loading size="small" text="" showText={false} />
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

MessageList.propTypes = {
  messages: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired,
  messagesEndRef: PropTypes.object.isRequired,
  onSampleQuestionClick: PropTypes.func
};

export default MessageList;

