import './index.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { NotificationProvider } from './components/common/NotificationProvider';
import SessionManager from './SessionManager'; // Ajusta el path si es necesario

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <NotificationProvider>
      <SessionManager />
      <App />
    </NotificationProvider>
  </BrowserRouter>
);
