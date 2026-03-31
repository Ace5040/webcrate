import { createApp } from 'vue'
import { i18n } from './i18n.js'
import axios from 'axios'
import VueAxios from 'vue-axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/common.scss'
import './styles/admin.scss'
import Page from './pages/admin-projects.vue'

const app = createApp(Page)
app.use(i18n)
app.use(VueAxios, axios)
app.mount('#app')
