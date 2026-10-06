import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The FastAPI backend runs on port 8000 by default (uvicorn's standard port).
// BACKEND_URL can point the proxy elsewhere if that port is taken.
const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': backendUrl,
      '/media': backendUrl,
    },
  },
})
