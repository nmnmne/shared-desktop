import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      // Прокси для конкретного эндпоинта
      '/api/v1/traffic-lights/get-state': {
        target: 'http://192.168.45.93:8001', // Целевой сервер
        changeOrigin: true, // Меняет origin на целевой сервер
        secure: false, // Отключает проверку SSL (если используется HTTP)
        rewrite: (path) => path.replace(/^\/api\/v1\/traffic-lights\/get-state-test/, '/api/v1/traffic-lights/get-state-test'),
      },
    },
  },
});


// import { fileURLToPath, URL } from 'node:url'

// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'


// export default defineConfig({
//   plugins: [
//     vue(),
//     vueDevTools(),
//   ],
//   resolve: {
//     alias: {
//       '@': fileURLToPath(new URL('./src', import.meta.url))
//     },
//   },
// })
