import 'es6-promise/auto'
import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(Vuex)
Vue.use(VueAxios, axios)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import './styles/common.scss'
import './styles/admin.scss'
const store = new Vuex.Store({
  state: {
    user: user,
    actual: actual
  },
  mutations: {
    setActual(state, value) {
      state.actual = value;
    }
  }
})

import header from './components/header.vue';
new (Vue.extend(header))({
  el: '#header',
  store
});

import page from './pages/admin-projects.vue';
new (Vue.extend(page))({
  el: '#app',
  store
});
