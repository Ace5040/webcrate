import { createApp } from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/common.scss'
import './styles/admin.scss'
import Page from './pages/admin-redirects.vue'

const app = createApp(Page)
app.use(VueAxios, axios)
app.mount('#app')
