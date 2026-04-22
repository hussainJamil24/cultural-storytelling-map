import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

// creates the react root from the html mount node
const root = ReactDOM.createRoot(document.getElementById('root'));

// renders the app inside react strict mode
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
