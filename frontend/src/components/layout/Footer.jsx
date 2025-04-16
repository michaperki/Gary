
// src/components/layout/Footer.jsx
import React from 'react';
import PropTypes from 'prop-types';

const Footer = ({ version }) => {
  return (
    <footer className="app-footer">
      <p>
        Clinical Trials AI Assistant • Powered by Vector Search and LLM Technology
        {version && ` • v${version}`}
      </p>
    </footer>
  );
};

Footer.propTypes = {
  version: PropTypes.string
};

export default Footer;

