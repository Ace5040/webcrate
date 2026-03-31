import { createApp } from 'vue'
import { i18n } from './i18n.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/common.scss'
import Login from './pages/login.vue'

const app = createApp(Login)
app.use(i18n)
app.mount('#app')
