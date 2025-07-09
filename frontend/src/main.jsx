import './index.css';                    // Importa los estilos globales
import React from 'react';               // Importa React
import ReactDOM from 'react-dom/client'; // Para renderizar con la API moderna
import { BrowserRouter } from 'react-router-dom'; // Enrutamiento
import App from './App';                 // Componente raíz de tu aplicación
import { NotificationProvider } from './components/common/NotificationProvider'; // Ajusta el path si es necesario

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <NotificationProvider>
      <App />
    </NotificationProvider>
  </BrowserRouter>
);
