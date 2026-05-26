import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Gracefully swallow benign Vite HMR websocket connection failures to avoid noisy overlays
if (typeof window !== 'undefined') {
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason;
    const isWebsocketError = 
      (reason && typeof reason.message === 'string' && /websocket|ws/i.test(reason.message)) ||
      (typeof reason === 'string' && /websocket|ws/i.test(reason)) ||
      (reason && typeof reason === 'object' && String(reason).toLowerCase().includes('websocket'));
      
    if (isWebsocketError) {
      event.preventDefault();
      event.stopPropagation();
    }
  });

  window.addEventListener('error', (event) => {
    const isWebsocketError = 
      (event.message && /websocket|ws/i.test(event.message)) ||
      (event.error && typeof event.error.message === 'string' && /websocket|ws/i.test(event.error.message)) ||
      (event.error && String(event.error).toLowerCase().includes('websocket'));
      
    if (isWebsocketError) {
      event.preventDefault();
      event.stopPropagation();
    }
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

