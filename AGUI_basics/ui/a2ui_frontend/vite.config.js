import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002,
    strictPort: true,
    open: true,
    proxy: {
      '/a2ui-events': {
        target: 'http://localhost:8502',
        changeOrigin: true,
      },
    },
  },
});
