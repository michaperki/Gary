// src/index.js - Application entry point
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { logger } from './utils/logger';

// Log application start
logger.info('Application starting...');

// Create root and render app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Log application mounted
logger.info('Application mounted');
