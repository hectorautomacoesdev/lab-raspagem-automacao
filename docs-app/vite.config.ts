import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// base relativo p/ funcionar em GitHub Pages (subpasta) e local
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  server: {
    // permite importar os .md da pasta irmã ../docs
    fs: { allow: ['..'] },
  },
})
