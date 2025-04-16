// src/hooks/useChat.js - Custom hook for chat functionality
import { useContext, useRef, useEffect } from 'react';
import ChatContext from '../context/ChatContext';

export const useChat = () => {
  // Get chat context
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  
  // Create ref for scrolling to bottom of messages
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [context.messages]);
  
  return {
    ...context,
    messagesEndRef
  };
};

export default useChat;

