import { createApp } from 'vue'
import { i18n } from './i18n.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './styles/common.scss'
import './styles/admin.scss'
import Header from './components/header.vue'

const app = createApp(Header)
app.use(i18n)
app.mount('#header')
