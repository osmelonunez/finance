import './index.css';                    // Importa los estilos globales
import React from 'react';              // Importa React
import ReactDOM from 'react-dom/client'; // Para renderizar con la API moderna
import { BrowserRouter } from 'react-router-dom'; // Enrutamiento
import App from './App';                // Componente raíz de tu aplicación

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
