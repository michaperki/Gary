
// src/components/search/TrialCard.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { formatDate, formatPhase, formatGender, formatBoolean } from '../../utils/formatter';

const TrialCard = ({ trial }) => {
  return (
    <div className="trial-card">
      <h3 className="trial-title">{trial.title}</h3>
      
      <div className="trial-details">
        <div className="trial-detail">
          <span className="detail-label">NCT ID:</span>
          <span className="detail-value">{trial.nct_id}</span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Principal Investigator:</span>
          <span className="detail-value">
            {trial.principal_investigator || 'Not specified'}
          </span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Phase:</span>
          <span className="detail-value">{formatPhase(trial.phase)}</span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Eligibility:</span>
          <span className="detail-value">
            {formatGender(trial.gender)} • {trial.age_range || 'Age not specified'}
          </span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Healthy Volunteers:</span>
          <span className="detail-value">
            {formatBoolean(trial.healthy_volunteers, 'Accepted', 'Not Accepted')}
          </span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Conditions:</span>
          <span className="detail-value">{trial.conditions || 'Not specified'}</span>
        </div>
        
        <div className="trial-detail">
          <span className="detail-label">Interventions:</span>
          <span className="detail-value">{trial.interventions || 'Not specified'}</span>
        </div>
      </div>
      
      <div className="trial-actions">
        <a 
          href={trial.source_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="view-details-btn"
        >
          View on ClinicalTrials.gov
        </a>
      </div>
    </div>
  );
};

TrialCard.propTypes = {
  trial: PropTypes.shape({
    title: PropTypes.string.isRequired,
    nct_id: PropTypes.string,
    principal_investigator: PropTypes.string,
    phase: PropTypes.string,
    gender: PropTypes.string,
    age_range: PropTypes.string,
    healthy_volunteers: PropTypes.string,
    conditions: PropTypes.string,
    interventions: PropTypes.string,
    source_url: PropTypes.string.isRequired
  }).isRequired
};

export default TrialCard;

