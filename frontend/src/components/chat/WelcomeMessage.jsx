
// src/components/chat/WelcomeMessage.jsx
import React from 'react';
import PropTypes from 'prop-types';

const SAMPLE_QUESTIONS = [
  "What clinical trials are available for melanoma patients who failed immunotherapy?",
  "Are there any phase 2 trials for EGFR-positive lung cancer patients?",
  "Tell me about trials accepting healthy volunteers for vaccine studies"
];

const WelcomeMessage = ({ onSampleQuestionClick }) => {
  return (
    <div className="welcome-message">
      <h2>Welcome to the Clinical Trials AI Assistant</h2>
      
      <p>
        Ask me questions about clinical trials and I'll help you find relevant 
        information for your patients.
      </p>
      
      <div className="sample-questions">
        <p>Examples:</p>
        <ul>
          {SAMPLE_QUESTIONS.map((question, index) => (
            <li 
              key={index}
              onClick={() => onSampleQuestionClick && onSampleQuestionClick(question)}
              className="sample-question"
            >
              "{question}"
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

WelcomeMessage.propTypes = {
  onSampleQuestionClick: PropTypes.func
};

export default WelcomeMessage;

