import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

function buildSymfonyManifest(outDir) {
  return {
    name: 'symfony-manifest',
    closeBundle() {
      const files = fs.existsSync(outDir) ? fs.readdirSync(outDir) : []
      const manifest = {}

      files.forEach((file) => {
        if (!file.endsWith('.js') && !file.endsWith('.css')) {
          return
        }

        const key = file.replace(/\.(js|css)$/u, '')
        manifest[key] = `/${file}`
      })

      fs.writeFileSync(
        resolve(outDir, 'manifest.json'),
        JSON.stringify(manifest, null, 2)
      )
    }
  }
}

export default defineConfig({
  plugins: [
    vue(),
    buildSymfonyManifest(resolve(__dirname, '../../public/build'))
  ],
  build: {
    outDir: resolve(__dirname, '../../public/build'),
    emptyOutDir: true,
    cssCodeSplit: false,
    manifest: false,
    rollupOptions: {
      input: {
        login: resolve(__dirname, 'src/login.js'),
        admin: resolve(__dirname, 'src/admin.js'),
        'admin-projects': resolve(__dirname, 'src/admin-projects.js'),
        'admin-project': resolve(__dirname, 'src/admin-project.js'),
        'admin-redirects': resolve(__dirname, 'src/admin-redirects.js'),
        'admin-redirect': resolve(__dirname, 'src/admin-redirect.js'),
        header: resolve(__dirname, 'src/header.js'),
        icons: resolve(__dirname, 'src/icons/icons.js')
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'style.css') {
            return 'style.css'
          }

          return '[name].[ext]'
        },
        manualChunks(id) {
          if (id.includes('node_modules/bootstrap/dist/js/bootstrap.bundle')) {
            return 'bootstrap.bundle.min'
          }

          if (id.includes('node_modules/vue-axios')) {
            return 'vue-axios.esm.min'
          }

          if (
            id.includes('/src/styles/') ||
            id.includes('bootstrap/dist/css/bootstrap.min.css')
          ) {
            return 'style'
          }

          if (
            id.includes('node_modules/jquery') ||
            id.includes('node_modules/sortablejs')
          ) {
            return 'common'
          }
        }
      }
    }
  }
})
