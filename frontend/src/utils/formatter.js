
// src/utils/formatter.js - Data formatting utilities
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString; // Return original string if parsing fails
  }
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength).trim()}...`;
};

export const formatPhase = (phase) => {
  if (!phase) return 'Not Specified';
  
  // Handle common phase formats
  if (phase.toLowerCase() === 'n/a') return 'Not Applicable';
  if (phase.toLowerCase() === 'early phase 1') return 'Early Phase 1';
  
  return phase;
};

export const formatGender = (gender) => {
  if (!gender) return 'Not Specified';
  
  const genderMap = {
    'ALL': 'All Genders',
    'MALE': 'Male',
    'FEMALE': 'Female',
  };
  
  return genderMap[gender.toUpperCase()] || gender;
};

export const formatBoolean = (value, trueText = 'Yes', falseText = 'No') => {
  if (value === null || value === undefined) return 'Not Specified';
  
  if (typeof value === 'string') {
    if (value.toLowerCase() === 'yes' || value.toLowerCase() === 'true') return trueText;
    if (value.toLowerCase() === 'no' || value.toLowerCase() === 'false') return falseText;
    return value;
  }
  
  return value ? trueText : falseText;
};
