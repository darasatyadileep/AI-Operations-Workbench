import { defineConfig } from 'vite';

export default defineConfig({
  base: '/AI-Operations-Workbench/',
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api/compressor': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: p => p.replace(/^\/api\/compressor/, '')
      },
      '/api/optimizer': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: p => p.replace(/^\/api\/optimizer/, '')
      },
      '/api/vision': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: p => p.replace(/^\/api\/vision/, '')
      },
      '/api/intelligence': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: p => p.replace(/^\/api\/intelligence/, '')
      }
    }
  }
});
