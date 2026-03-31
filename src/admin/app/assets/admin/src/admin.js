import { createApp } from 'vue'
import { i18n } from './i18n.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/common.scss'
import './styles/admin.scss'
import Page from './pages/admin.vue'

const app = createApp(Page)
app.use(i18n)
app.mount('#app')
