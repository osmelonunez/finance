import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path'; // <- AÑADIDO

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // <- AÑADIDO
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': 'http://backend:3001',
    },
  },
});
