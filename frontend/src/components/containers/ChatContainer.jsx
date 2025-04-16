// src/components/containers/ChatContainer.jsx
import React, { useState } from 'react';
import MessageList from '../chat/MessageList';
import ChatInput from '../chat/ChatInput';
import useChat from '../../hooks/useChat';
import useApi from '../../hooks/useApi';

const ChatContainer = () => {
  // Get chat functionality from hook
  const { 
    messages, 
    isLoading, 
    error, 
    sendMessage, 
    startNewConversation,
    messagesEndRef
  } = useChat();
  
  // Get API connection status
  const { isConnected } = useApi();
  
  // Handle sample question clicks
  const handleSampleQuestionClick = (question) => {
    sendMessage(question);
  };
  
  // Handle sending messages
  const handleSendMessage = (message) => {
    sendMessage(message);
  };
  
  // Handle starting a new chat
  const handleNewChat = () => {
    startNewConversation();
  };
  
  return (
    <div className="chat-container">
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}
      
      <MessageList
        messages={messages}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
        onSampleQuestionClick={handleSampleQuestionClick}
      />
      
      <ChatInput
        onSendMessage={handleSendMessage}
        onNewChat={handleNewChat}
        isLoading={isLoading}
        isDisabled={!isConnected}
        hasMessages={messages.length > 0}
      />
    </div>
  );
};

export default ChatContainer;
