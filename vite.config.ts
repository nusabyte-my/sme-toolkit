import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  return {
    server: {
      port: 5340,
      host: '0.0.0.0',
      proxy: {
        '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
        '/auth': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      },
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    },
    // Performance optimizations
    build: {
      // Code splitting configuration
      rollupOptions: {
        output: {
          // Manual chunks for better caching and parallel loading
          manualChunks: {
            // React and React DOM
            'react-vendor': ['react', 'react-dom'],
            // UI library
            'lucide-react': ['lucide-react'],
            // Markdown processing
            'markdown': ['react-markdown'],
            // PDF generation
            'pdf': ['jspdf'],
            // Canvas to image
            'canvas': ['html2canvas'],
            // AI SDK
            'ai-sdk': ['@google/genai'],
          },
          // Chunk file naming for better caching
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
        },
      },
      // Optimize chunk size
      chunkSizeWarningLimit: 1000,
      // Minify CSS
      cssCodeSplit: true,
      // Source maps for production (optional, set to false for smaller bundles)
      sourcemap: mode === 'development',
    },
    // Optimize dependencies
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'lucide-react',
        'react-markdown',
        'jspdf',
        'html2canvas',
        '@google/genai',
      ],
    },
    // Preload critical resources
    preview: {
      headers: {
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    },
  };
});
