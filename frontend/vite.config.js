import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})


// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// export default defineConfig({
//   plugins: [react()],
//   server: {
//     port: 3000,
//     host: '0.0.0.0',
//     proxy: {
//       '/api': {
//         target: 'http://101.132.193.95:8000', 
//         changeOrigin: true,
//         secure: false,
//         // 不需要rewrite，后端路由已经包含/api前缀
//       }
//     }
//   }
// })
