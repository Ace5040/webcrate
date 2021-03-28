import 'es6-promise/auto'
import Vue from 'vue'
import Vuex from 'vuex'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(Vuex)
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
  store: store
});

import page from './pages/admin.vue';
new (Vue.extend(page))({
  el: '#app',
  store
});
