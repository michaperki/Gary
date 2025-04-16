
// src/api/services/trialService.js
import apiClient from '../apiClient';
import ENDPOINTS from '../endpoints';

export const searchTrials = async (query, filters = {}) => {
  const params = new URLSearchParams({ q: query });
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  
  try {
    const response = await apiClient.get(`${ENDPOINTS.TRIALS_SEARCH}?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error searching trials:', error);
    throw error;
  }
};

export const getFilterOptions = async () => {
  try {
    const response = await apiClient.get(ENDPOINTS.TRIALS_FILTERS);
    return response.data;
  } catch (error) {
    console.error('Error fetching filter options:', error);
    throw error;
  }
};

export const getTrialById = async (trialId) => {
  try {
    const response = await apiClient.get(ENDPOINTS.TRIAL_BY_ID(trialId));
    return response.data;
  } catch (error) {
    console.error(`Error fetching trial ${trialId}:`, error);
    throw error;
  }
};
