import { createApp } from 'vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './styles/common.scss'
import './styles/admin.scss'
import Header from './components/header.vue'

createApp(Header).mount('#header')
