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
import Page from './pages/admin-project.vue'

window.$ = $
window.jQuery = $

const app = createApp(Page)
app.use(i18n)
app.use(VueAxios, axios)
app.mount('#app')

function updateBackendOptions(selectedTemplate, preserveValue) {
  const backendSelect = document.getElementById('project_backend')

  if (!backendSelect) {
    return
  }

  const currentValue = preserveValue !== undefined ? preserveValue : backendSelect.value

  backendSelect.innerHTML = '<option value="">Loading...</option>'
  backendSelect.disabled = true

  $.ajax({
    url: '/admin/api/backends',
    method: 'GET',
    data: {
      template: selectedTemplate
    },
    success(data) {
      backendSelect.innerHTML = ''

      data.forEach((backend) => {
        const option = document.createElement('option')
        option.value = backend.id
        option.text = backend.fullName
        backendSelect.appendChild(option)
      })

      if (currentValue) {
        backendSelect.value = currentValue
      }

      backendSelect.disabled = false
    },
    error(xhr, status, error) {
      console.error('Error fetching backends:', error)
      backendSelect.innerHTML = '<option value="">Error loading backends</option>'
      backendSelect.disabled = false
    }
  })
}

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
  const nginxTemplateSelect = document.getElementById('project_nginx_template')

  if (nginxTemplateSelect) {
    updateBackendOptions(nginxTemplateSelect.value)

    $('#project_nginx_template').on('change', function () {
      updateBackendOptions($(this).val())
    })
  }

  setupNameValidation(
    'project_name',
    '/admin/api/check-project-name',
    'excludeUid',
    () => document.getElementById('project_uid')?.value || ''
  )
})

const projectDomains = document.getElementById('project_domains')
if (projectDomains) {
  Sortable.create(projectDomains, {
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
    onEnd() {
      $('#project_domains .form-group').each((index, item) => {
        $('input', item).attr('name', 'project[domains][' + index + ']')
      })
    }
  })
}

$('body').on('click', '.add-domain-button', () => {
  const list = $('#project_domains')
  const counter = list.children().length
  let newWidget = list.attr('data-prototype')
  newWidget = newWidget.replace(/__name__/g, counter)
  $(newWidget).appendTo(list)
})

$('body #project_domains').on('click', '.remove', (e) => {
  const list = $('#project_domains')
  const counter = list.children().length
  if (counter > 1) {
    $(e.currentTarget).parent().remove()
    $('#project_domains .form-group').each((index, item) => {
      $('input', item).attr('name', 'project[domains][' + index + ']')
    })
  }
})

const projectNginxOptions = document.getElementById('project_nginx_options')
if (projectNginxOptions) {
  Sortable.create(projectNginxOptions, {
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
    onEnd() {
      $('#project_nginx_options > .form-group').each((groupindex, group) => {
        $('input', group).each((index, input) => {
          let name = $(input).attr('name').split('[')
          name = name[name.length - 1].replace(']', '')
          $(input).attr('name', 'project[nginx_options][' + groupindex + '][' + name + ']')
        })
      })
    }
  })
}

$('body').on('click', '.add-nginx-option-button', () => {
  const list = $('#project_nginx_options')
  const counter = list.children().length
  let newWidget = list.attr('data-prototype')
  newWidget = newWidget.replace(/__name__/g, counter)
  $(newWidget).appendTo(list)
})

$('body #project_nginx_options').on('click', '.remove', (e) => {
  const list = $('#project_nginx_options')
  const counter = list.children().length
  if (counter > 0) {
    $(e.currentTarget).parent().remove()
    $('#project_nginx_options > .form-group').each((groupindex, group) => {
      $('input', group).each((index, input) => {
        let name = $(input).attr('name').split('[')
        name = name[name.length - 1].replace(']', '')
        $(input).attr('name', 'project[nginx_options][' + groupindex + '][' + name + ']')
      })
    })
  }
})

const projectAuthLocations = document.getElementById('project_auth_locations')
if (projectAuthLocations) {
  Sortable.create(projectAuthLocations, {
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
    onEnd() {
      $('#project_auth_locations > .form-group').each((groupindex, group) => {
        $('input', group).each((index, input) => {
          let name = $(input).attr('name').split('[')
          name = name[name.length - 1].replace(']', '')
          $(input).attr('name', 'project[auth_locations][' + groupindex + '][' + name + ']')
        })
      })
    }
  })
}

$('body').on('click', '.add-auth-location-button', () => {
  const list = $('#project_auth_locations')
  const counter = list.children().length
  let newWidget = list.attr('data-prototype')
  newWidget = newWidget.replace(/__name__/g, counter)
  $(newWidget).appendTo(list)
})

$('body #project_auth_locations').on('click', '.remove', (e) => {
  const list = $('#project_auth_locations')
  const counter = list.children().length
  if (counter > 0) {
    $(e.currentTarget).parent().remove()
    $('#project_auth_locations > .form-group').each((groupindex, group) => {
      $('input', group).each((index, input) => {
        let name = $(input).attr('name').split('[')
        name = name[name.length - 1].replace(']', '')
        $(input).attr('name', 'project[auth_locations][' + groupindex + '][' + name + ']')
      })
    })
  }
})

const projectDuplicityFilters = document.getElementById('project_DuplicityFilters')
if (projectDuplicityFilters) {
  Sortable.create(projectDuplicityFilters, {
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
    onEnd() {
      $('#project_DuplicityFilters > .form-group').each((groupindex, group) => {
        $('input,select', group).each((index, input) => {
          let name = $(input).attr('name').split('[')
          name = name[name.length - 1].replace(']', '')
          $(input).attr('name', 'project[DuplicityFilters][' + groupindex + '][' + name + ']')
        })
      })
    }
  })
}

$('body').on('click', '.add-duplicity-filter-button', () => {
  const list = $('#project_DuplicityFilters')
  const counter = list.children().length
  let newWidget = list.attr('data-prototype')
  newWidget = newWidget.replace(/__name__/g, counter)
  $(newWidget).appendTo(list)
})

$('body #project_DuplicityFilters').on('click', '.remove', (e) => {
  const list = $('#project_DuplicityFilters')
  const counter = list.children().length
  if (counter > 0) {
    $(e.currentTarget).parent().remove()
    $('#project_DuplicityFilters > .form-group').each((groupindex, group) => {
      $('input,select', group).each((index, input) => {
        let name = $(input).attr('name').split('[')
        name = name[name.length - 1].replace(']', '')
        $(input).attr('name', 'project[DuplicityFilters][' + groupindex + '][' + name + ']')
      })
    })
  }
})
