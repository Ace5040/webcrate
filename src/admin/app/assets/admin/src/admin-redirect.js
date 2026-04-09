import { createApp } from 'vue'
import { i18n } from './i18n.js'
const t = (key) => i18n.global.t(key)
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

function setupNameValidation(inputId, checkUrl, excludeParam, excludeValue) {
  const input = document.getElementById(inputId)
  if (!input) return
  const pattern = /^[a-z][a-z0-9]*$/
  let timer = null

  function setValidity(state, message) {
    input.classList.remove('is-valid', 'is-invalid')
    input.closest('.form-group')?.querySelectorAll('.dynamic-feedback').forEach(el => el.remove())
    if (state === 'valid') {
      input.classList.add('is-valid')
    } else if (state === 'invalid') {
      input.classList.add('is-invalid')
      const fb = document.createElement('div')
      fb.className = 'invalid-feedback dynamic-feedback'
      fb.textContent = message
      input.insertAdjacentElement('afterend', fb)
    }
  }

  input.addEventListener('input', () => {
    clearTimeout(timer)
    const val = input.value
    if (!val) {
      input.classList.remove('is-valid', 'is-invalid')
      input.closest('.form-group')?.querySelectorAll('.dynamic-feedback').forEach(el => el.remove())
      return
    }
    if (!pattern.test(val)) {
      setValidity('invalid', t('form.validation.nameInvalid'))
      return
    }
    timer = setTimeout(() => {
      const params = { name: val }
      if (excludeValue()) params[excludeParam] = excludeValue()
      $.get(checkUrl, params, (data) => {
        if (input.value !== val) return
        setValidity(data.available ? 'valid' : 'invalid', data.available ? '' : t('form.validation.nameTaken'))
      })
    }, 400)
  })
}

$(document).ready(() => {
  const nameInput = document.getElementById('redirect_name')
  const originalName = nameInput?.value || ''
  setupNameValidation(
    'redirect_name',
    '/admin/api/check-redirect-name',
    'excludeName',
    () => originalName
  )
})

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
