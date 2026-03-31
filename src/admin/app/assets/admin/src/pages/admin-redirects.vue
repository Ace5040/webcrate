<template>
<div class="admin-page">
  <div class="page-header">
    <h1>{{ t('redirects.title') }}</h1>
    <div class="page-actions">
      <form @submit.prevent="onImport" class="import-form">
        <input class="form-control form-control-sm" type="file" @change="onFileChange">
        <button type="submit" class="btn btn-sm btn-outline-secondary">{{ t('common.import') }}</button>
      </form>
      <a href="/admin/redirect/add" class="btn btn-sm btn-accent">
        <i class="bi bi-plus-lg me-1"></i>{{ t('redirects.newRedirect') }}
      </a>
      <div v-if="applying" class="spinner-border spinner-border-sm text-secondary" role="status"></div>
    </div>
  </div>

  <div class="app-card position-relative">
    <div class="app-table-wrap">
      <table v-if="redirects.length" class="app-table">
        <thead>
          <tr>
            <th>{{ t('common.name') }}</th>
            <th>{{ t('redirects.url') }}</th>
            <th>{{ t('common.https') }}</th>
            <th>{{ t('common.status') }}</th>
            <th>{{ t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in redirects" :key="item.name">
            <td class="name-cell">{{ item.name }}</td>
            <td>{{ item.url }}</td>
            <td>{{ item.https }}</td>
            <td>
              <span class="status-badge" :class="item.active ? 'active' : 'inactive'">
                {{ item.active ? t('common.active') : t('common.inactive') }}
              </span>
            </td>
            <td>
              <div class="row-actions">
                <a class="btn btn-sm btn-outline-primary" :href="'/admin/redirect/' + item.name">{{ t('common.edit') }}</a>
                <button class="btn btn-sm btn-outline-danger" type="button" @click="onDelete(item.name)">{{ t('common.delete') }}</button>
                <button
                  v-if="item.active == false"
                  class="btn btn-sm btn-outline-success"
                  type="button"
                  @click="onActivate(item.name)"
                >{{ t('common.activate') }}</button>
                <button
                  v-if="item.active"
                  class="btn btn-sm btn-outline-secondary"
                  type="button"
                  @click="onDeactivate(item.name)"
                >{{ t('common.deactivate') }}</button>
                <button
                  v-if="!item.actual"
                  class="btn btn-sm btn-outline-warning"
                  type="button"
                  @click="onApply(item)"
                >
                  {{ t('common.apply') }}
                  <span v-if="item.applying" class="spinner-border spinner-border-sm ms-1"></span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="busy" class="table-overlay">
      <div v-if="processing" class="overlay-processing">
        <div class="processing-label">{{ t('common.processing') }}</div>
        <div class="progress">
          <div class="progress-bar" :style="{ width: (counter * 5) + '%' }"></div>
        </div>
      </div>
      <div v-else class="overlay-confirm">
        <p>{{ t('common.areYouSure') }}</p>
        <div class="confirm-actions">
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="onCancel">{{ t('common.cancel') }}</button>
          <button type="button" class="btn btn-sm btn-accent" @click="onOK">{{ t('common.confirm') }}</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { appContext } = getCurrentInstance()
const axios = appContext.config.globalProperties.axios

const busy = ref(false)
const processing = ref(false)
const applying = ref(false)
const counter = ref(1)
const interval = ref(null)
const selectedName = ref(null)
const redirects = ref(window.redirects || [])
const redirectsFile = ref(null)

function onFileChange(event) {
  redirectsFile.value = event.target.files?.[0] || null
}

function clearTimer() {
  if (interval.value) {
    clearInterval(interval.value)
    interval.value = null
  }
}

function finishOverlay() {
  clearTimer()
  busy.value = false
  processing.value = false
  selectedName.value = null
}

function startProgress(callback) {
  counter.value = 1
  processing.value = true
  clearTimer()
  interval.value = setInterval(() => {
    if (counter.value < 20) {
      counter.value += 1
      return
    }

    callback()
  }, 150)
}

function onImport() {
  if (!redirectsFile.value) {
    return
  }

  const formData = new FormData()
  formData.append('file', redirectsFile.value)

  axios.post('/admin/import-redirects', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then((response) => {
    const data = response.data
    if (data && data.result === 'ok' && data.redirects) {
      redirects.value = data.redirects
    }
  }).catch(() => {
    console.log('FAILURE!!')
  })
}

function onDelete(name) {
  selectedName.value = name
  processing.value = false
  busy.value = true
}

function onCancel() {
  busy.value = false
  selectedName.value = null
}

function onOK() {
  startProgress(() => {
    axios.get('/admin/redirect/' + selectedName.value + '/delete')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.redirects) {
          redirects.value = data.redirects
        }
        finishOverlay()
      })
      .catch(() => {
        console.log('FAILURE!!')
        finishOverlay()
      })
  })
}

function onApply(item) {
  if (item.applying) {
    return
  }

  item.applying = true
  axios.get('/admin/redirect/' + item.name + '/reload')
    .then((response) => {
      const data = response.data
      if (data && data.result === 'ok') {
        item.applying = false
        redirects.value = data.redirects
      }
    })
    .catch(() => {
      item.applying = false
      console.log('FAILURE!!')
    })
}

function onActivate(name) {
  selectedName.value = name
  busy.value = true
  startProgress(() => {
    axios.get('/admin/redirect/' + selectedName.value + '/activate')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.redirects) {
          redirects.value = data.redirects
        }
        finishOverlay()
      })
      .catch(() => {
        console.log('FAILURE!!')
        finishOverlay()
      })
  })
}

function onDeactivate(name) {
  selectedName.value = name
  busy.value = true
  startProgress(() => {
    axios.get('/admin/redirect/' + selectedName.value + '/deactivate')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.redirects) {
          redirects.value = data.redirects
        }
        finishOverlay()
      })
      .catch(() => {
        console.log('FAILURE!!')
        finishOverlay()
      })
  })
}
</script>
