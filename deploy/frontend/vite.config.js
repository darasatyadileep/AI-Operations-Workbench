import { defineConfig } from 'vite';

export default defineConfig({
  base: '/',
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api/compressor': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/api/optimizer': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/api/vision': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/api/intelligence': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
