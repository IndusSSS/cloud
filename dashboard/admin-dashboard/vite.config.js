// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,        // listen on 0.0.0.0 so it’s reachable externally
    port: 5173,        // your dev port
    proxy: {
      // proxy all /v1 requests to your FastAPI
      '/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,          // if you’re using HTTPS on FastAPI, set up accordingly
        rewrite: (path) => path // leave the path intact
      }
    }
  }
})
