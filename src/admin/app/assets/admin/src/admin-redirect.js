import { createApp } from 'vue'
import { i18n } from './i18n.js'
import axios from 'axios'
import VueAxios from 'vue-axios'
import Sortable from 'sortablejs'
import $ from 'jquery'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './styles/common.scss'
import './styles/admin.scss'
import Page from './pages/admin-redirect.vue'

window.$ = $
window.jQuery = $

const app = createApp(Page)
app.use(i18n)
app.use(VueAxios, axios)
app.mount('#app')

const redirectDomains = document.getElementById('redirect_domains')
if (redirectDomains) {
  Sortable.create(redirectDomains, {
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
    onEnd() {
      $('#redirect_domains .form-group').each((index, item) => {
        $('input', item).attr('name', 'redirect[domains][' + index + ']')
      })
    }
  })
}

$('body').on('click', '.add-domain-button', () => {
  const list = $('#redirect_domains')
  const counter = list.children().length
  let newWidget = list.attr('data-prototype')
  newWidget = newWidget.replace(/__name__/g, counter)
  $(newWidget).appendTo(list)
})

$('body #redirect_domains').on('click', '.remove', (e) => {
  const list = $('#redirect_domains')
  const counter = list.children().length
  if (counter > 1) {
    $(e.currentTarget).parent().remove()
    $('#redirect_domains .form-group').each((index, item) => {
      $('input', item).attr('name', 'redirect[domains][' + index + ']')
    })
  }
})
