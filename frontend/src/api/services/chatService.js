
// src/api/services/chatService.js
import apiClient from '../apiClient';
import ENDPOINTS from '../endpoints';

export const sendChatMessage = async (message, conversationId = null, userId = 'user123') => {
  try {
    const response = await apiClient.post(ENDPOINTS.CHAT, {
      message,
      conversation_id: conversationId,
      user_id: userId
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getConversation = async (conversationId) => {
  try {
    const response = await apiClient.get(ENDPOINTS.CONVERSATION_BY_ID(conversationId));
    return response.data;
  } catch (error) {
    console.error('Error loading conversation:', error);
    throw error;
  }
};

export const getConversations = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.CONVERSATIONS);
    return response.data;
  } catch (error) {
    console.error('Error loading conversations:', error);
    throw error;
  }
};

