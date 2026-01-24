import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    define: {
      'process.env': env
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      allowedHosts: ['frontend.wled-manager.orb.local'],
      proxy: {
        '/api': {
          target: `${env.VITE_API_PROTOCOL}://${env.VITE_API_HOST}:${env.VITE_API_PORT}`,
          changeOrigin: true
        }
      }
    }
  }
})
