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

$(document).ready(() => {
  const nginxTemplateSelect = document.getElementById('project_nginx_template')

  if (nginxTemplateSelect) {
    updateBackendOptions(nginxTemplateSelect.value)

    $('#project_nginx_template').on('change', function () {
      updateBackendOptions($(this).val())
    })
  }
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
