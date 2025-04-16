// src/context/ChatContext.jsx - Context for managing chat state and operations
import React, { createContext, useState, useContext, useCallback, useEffect, useRef } from 'react';
import { sendChatMessage, getConversation } from '../api';
import ApiContext from './ApiContext';
import { logger } from '../utils/logger';

// Create context
export const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  // State for chat
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  
  // Reference to store current conversation ID (needed for callbacks)
  const conversationIdRef = useRef(conversationId);
  
  // Get API connection status from context
  const { isConnected } = useContext(ApiContext);
  
  // Update ref when conversationId changes
  useEffect(() => {
    conversationIdRef.current = conversationId;
  }, [conversationId]);

  // Load a conversation by ID
  const loadConversation = useCallback(async (id) => {
    if (!id || !isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      logger.info(`Loading conversation: ${id}`);
      const data = await getConversation(id);
      
      if (data && data.messages) {
        setMessages(data.messages);
        setConversationId(data.conversation_id);
        logger.info(`Conversation loaded: ${data.conversation_id}`);
      } else {
        throw new Error('Invalid conversation data received');
      }
    } catch (err) {
      logger.error(`Error loading conversation ${id}:`, err);
      setError('Failed to load conversation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [isConnected]);

  // Send a message
  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || !isConnected) return;
    
    // Create user message object
    const userMessage = {
      role: 'user',
      content: messageText
    };
    
    // Add to messages immediately for better UX
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    
    try {
      logger.info('Sending message to chat API');
      const response = await sendChatMessage(
        messageText, 
        conversationIdRef.current
      );
      
      // Update conversation ID if new
      if (response.conversation_id && !conversationIdRef.current) {
        setConversationId(response.conversation_id);
      }
      
      // Create assistant message object
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        evidence: response.evidence
      };
      
      // Add assistant response to messages
      setMessages(prev => [...prev, assistantMessage]);
      logger.info('Message sent and response received');
      
      return assistantMessage;
    } catch (err) {
      logger.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message for better UX
      setMessages(prev => [
        ...prev, 
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
          isError: true
        }
      ]);
      
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [isConnected]);

  // Start a new conversation
  const startNewConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    logger.info('Started new conversation');
  }, []);

  // Context value
  const value = {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    loadConversation,
    startNewConversation
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatContext;
