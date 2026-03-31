<template>
<div class="admin-page">
  <div class="page-header">
    <h1>{{ t('projects.title') }}</h1>
    <div class="page-actions">
      <button class="btn btn-sm btn-outline-secondary" type="button" @click="openImportDialog">
        <i class="bi bi-upload me-1"></i>{{ t('common.import') }}
      </button>
      <a href="/admin/project/add" class="btn btn-sm btn-accent">
        <i class="bi bi-plus-lg me-1"></i>{{ t('projects.newProject') }}
      </a>
    </div>
  </div>

  <div class="app-card position-relative">
    <div class="app-table-wrap">
      <table v-if="projects.length" class="app-table">
        <thead>
          <tr>
            <th>{{ t('projects.uid') }}</th>
            <th>{{ t('common.name') }}</th>
            <th>{{ t('common.https') }}</th>
            <th>{{ t('projects.backend') }}</th>
            <th>{{ t('projects.template') }}</th>
            <th>{{ t('projects.backup') }}</th>
            <th>{{ t('common.status') }}</th>
            <th>{{ t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in projects" :key="item.uid">
            <td class="uid-cell">{{ item.uid }}</td>
            <td class="name-cell">{{ item.name }}</td>
            <td>{{ item.https }}</td>
            <td>{{ item.backend }}</td>
            <td>{{ item.template }}</td>
            <td>{{ item.backup }}</td>
            <td>
              <span class="status-badge" :class="item.active ? 'active' : 'inactive'">
                {{ item.active ? t('common.active') : t('common.inactive') }}
              </span>
            </td>
            <td>
              <div class="row-actions">
                <a class="btn btn-sm btn-outline-primary" :href="'/admin/project/' + item.uid">{{ t('common.edit') }}</a>
                <button class="btn btn-sm btn-outline-danger" type="button" @click="onDelete(item.uid)">{{ t('common.delete') }}</button>
                <button
                  v-if="item.active == false"
                  class="btn btn-sm btn-outline-success"
                  type="button"
                  @click="onActivate(item.uid)"
                >{{ t('common.activate') }}</button>
                <button
                  v-if="item.active"
                  class="btn btn-sm btn-outline-secondary"
                  type="button"
                  @click="onDeactivate(item.uid)"
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
                <button class="btn btn-sm btn-outline-info" type="button" @click="onRestart(item)">
                  {{ t('projects.restart') }}
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

<Teleport to="body">
  <Transition name="fade">
    <div v-if="showImportDialog" class="dialog-backdrop" @click.self="closeImportDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h2>{{ t('common.importDialogTitle') }}</h2>
          <button class="dialog-close" type="button" @click="closeImportDialog">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="onImport">
            <div class="mb-1">
              <label class="form-label">{{ t('common.selectFile') }}</label>
              <input ref="fileInputRef" class="form-control" type="file" @change="onFileChange">
            </div>
            <div class="dialog-actions">
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="closeImportDialog">{{ t('common.cancel') }}</button>
              <button type="submit" class="btn btn-sm btn-accent">{{ t('common.import') }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Transition>
</Teleport>
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
const selectedPid = ref(null)
const projects = ref(window.projects || [])
const projectsFile = ref(null)
const showImportDialog = ref(false)
const fileInputRef = ref(null)

function openImportDialog() {
  projectsFile.value = null
  showImportDialog.value = true
}

function closeImportDialog() {
  showImportDialog.value = false
  projectsFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function onFileChange(event) {
  projectsFile.value = event.target.files?.[0] || null
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
  selectedPid.value = null
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
  if (!projectsFile.value) {
    return
  }

  const formData = new FormData()
  formData.append('file', projectsFile.value)

  axios.post('/admin/import-projects', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then((response) => {
    const data = response.data
    if (data && data.result === 'ok' && data.projects) {
      projects.value = data.projects
      closeImportDialog()
    }
  }).catch(() => {
    console.log('FAILURE!!')
  })
}

function onDelete(pid) {
  selectedPid.value = pid
  processing.value = false
  busy.value = true
}

function onCancel() {
  busy.value = false
  selectedPid.value = null
}

function onOK() {
  startProgress(() => {
    axios.get('/admin/project/' + selectedPid.value + '/delete')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.projects) {
          projects.value = data.projects
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
  axios.get('/admin/project/' + item.uid + '/reload')
    .then((response) => {
      const data = response.data
      if (data && data.result === 'ok') {
        item.applying = false
        projects.value = data.projects
      }
    })
    .catch(() => {
      item.applying = false
      console.log('FAILURE!!')
    })
}

function onRestart(item) {
  if (item.applying) {
    return
  }

  item.applying = true
  axios.get('/admin/project/' + item.uid + '/restart')
    .then((response) => {
      const data = response.data
      if (data && data.result === 'ok') {
        item.applying = false
        projects.value = data.projects
      }
    })
    .catch(() => {
      item.applying = false
      console.log('FAILURE!!')
    })
}

function onActivate(pid) {
  selectedPid.value = pid
  busy.value = true
  startProgress(() => {
    axios.get('/admin/project/' + selectedPid.value + '/activate')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.projects) {
          projects.value = data.projects
        }
        finishOverlay()
      })
      .catch(() => {
        console.log('FAILURE!!')
        finishOverlay()
      })
  })
}

function onDeactivate(pid) {
  selectedPid.value = pid
  busy.value = true
  startProgress(() => {
    axios.get('/admin/project/' + selectedPid.value + '/deactivate')
      .then((response) => {
        const data = response.data
        if (data && data.result === 'ok' && data.projects) {
          projects.value = data.projects
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
