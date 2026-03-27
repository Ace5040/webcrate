import 'es6-promise/auto'
import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import Sortable from 'sortablejs'
import $ from 'jquery'
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
      actual: true
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

import page from './pages/admin-project.vue';
new (Vue.extend(page))({
    el: '#app'
});

// Function to update backend options based on selected nginx template
function updateBackendOptions(selectedTemplate) {
    const backendSelect = document.getElementById('project_backend');

    if (!backendSelect) {
        return;
    }

    // Show loading state
    backendSelect.innerHTML = '<option value="">Loading...</option>';
    backendSelect.disabled = true;

    // Make API call to get filtered backends
    $.ajax({
        url: '/admin/api/backends',
        method: 'GET',
        data: {
            template: selectedTemplate
        },
        success: function(data) {
            // Clear the select
            backendSelect.innerHTML = '';

            // Add the retrieved backends
            data.forEach(function(backend) {
                const option = document.createElement('option');
                option.value = backend.id;
                option.text = backend.fullName;
                backendSelect.appendChild(option);
            });

            backendSelect.disabled = false;
        },
        error: function(xhr, status, error) {
            console.error('Error fetching backends:', error);
            backendSelect.innerHTML = '<option value="">Error loading backends</option>';
            backendSelect.disabled = false;
        }
    });
}

// Initialize the backend filtering when the page loads
$(document).ready(function() {
    const nginxTemplateSelect = document.getElementById('project_nginx_template');

    if (nginxTemplateSelect) {
        // Initially load backends based on the current selection
        const initialTemplate = nginxTemplateSelect.value;
        updateBackendOptions(initialTemplate);

        // Add event listener to nginx template select
        $('#project_nginx_template').on('change', function() {
            const selectedTemplate = $(this).val();
            updateBackendOptions(selectedTemplate);
        });
    }
});

var el = document.getElementById('project_domains');
Sortable.create(el,{
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
	onEnd: function () {
        $('#project_domains .form-group').each( (index, item) => {
            $('input', item).attr('name', 'project[domains][' + index +']');
        });
    }
});

$('body').on('click', '.add-domain-button', e => {
    var list = $('#project_domains');
    var counter = list.children().length;
    var newWidget = list.attr('data-prototype');
    newWidget = newWidget.replace(/__name__/g, counter);
    $(newWidget).appendTo(list);
});

$('body #project_domains').on('click', '.remove', e => {
    var list = $('#project_domains');
    var counter = list.children().length;
    if ( counter > 1 ) {
        let item = e.currentTarget;
        $(item).parent().remove();
        $('#project_domains .form-group').each( (index, item) => {
            $('input', item).attr('name', 'project[domains][' + index +']');
        });
    }
});

var el = document.getElementById('project_nginx_options');
Sortable.create(el,{
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
	onEnd: function () {
        $('#project_nginx_options > .form-group').each( (groupindex, group) => {
            $('input', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[nginx_options][' + groupindex +'][' + name + ']');
            })
        })
    }
});

$('body').on('click', '.add-nginx-option-button', e => {
    var list = $('#project_nginx_options');
    var counter = list.children().length;
    var newWidget = list.attr('data-prototype');
    newWidget = newWidget.replace(/__name__/g, counter);
    $(newWidget).appendTo(list);
});

$('body #project_nginx_options').on('click', '.remove', e => {
    var list = $('#project_nginx_options');
    var counter = list.children().length;
    if ( counter > 0 ) {
        let item = e.currentTarget;
        $(item).parent().remove();
        $('#project_nginx_options > .form-group').each( (groupindex, group) => {
            $('input', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[nginx_options][' + groupindex +'][' + name + ']');
            })
        })
    }
});

var el = document.getElementById('project_auth_locations');
Sortable.create(el,{
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
	onEnd: function () {
        $('#project_auth_locations > .form-group').each( (groupindex, group) => {
            $('input', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[auth_locations][' + groupindex +'][' + name + ']');
            })
        })
    }
});

$('body').on('click', '.add-auth-location-button', e => {
    var list = $('#project_auth_locations');
    var counter = list.children().length;
    var newWidget = list.attr('data-prototype');
    newWidget = newWidget.replace(/__name__/g, counter);
    $(newWidget).appendTo(list);
});

$('body #project_auth_locations').on('click', '.remove', e => {
    var list = $('#project_auth_locations');
    var counter = list.children().length;
    if ( counter > 0 ) {
        let item = e.currentTarget;
        $(item).parent().remove();
        $('#project_auth_locations > .form-group').each( (groupindex, group) => {
            $('input', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[auth_locations][' + groupindex +'][' + name + ']');
            })
        })
    }
});

var el = document.getElementById('project_DuplicityFilters');
Sortable.create(el,{
    handle: '.handle',
    draggable: '.form-group',
    direction: 'vertical',
	onEnd: function () {
        $('#project_DuplicityFilters > .form-group').each( (groupindex, group) => {
            $('input,select', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[DuplicityFilters][' + groupindex +'][' + name + ']');
            })
        })
    }
});

$('body').on('click', '.add-duplicity-filter-button', e => {
    var list = $('#project_DuplicityFilters');
    var counter = list.children().length;
    var newWidget = list.attr('data-prototype');
    newWidget = newWidget.replace(/__name__/g, counter);
    $(newWidget).appendTo(list);
});

$('body #project_DuplicityFilters').on('click', '.remove', e => {
    var list = $('#project_DuplicityFilters');
    var counter = list.children().length;
    if ( counter > 0 ) {
        let item = e.currentTarget;
        $(item).parent().remove();
        $('#project_DuplicityFilters > .form-group').each( (groupindex, group) => {
            $('input,select', group).each( (index, input) => {
                let name = $(input).attr('name').split('[');
                name = name[name.length - 1].replace(']', '');
                $(input).attr('name', 'project[DuplicityFilters][' + groupindex +'][' + name + ']');
            })
        })
    }
});
