<template>
<div class="admin-page">
  <div class="action-menu clearfix">
    <div class="float-end">
      <form @submit.prevent="onImport">
        <div class="mb-2 d-flex align-items-center gap-2">
          <input class="form-control" type="file" @change="onFileChange">
          <button type="submit" class="btn btn-primary">Import</button>
        </div>
      </form>
    </div>
    <a href="/admin/project/add" class="btn btn-primary">Create new project</a>
    <div v-if="applying" class="spinner-border text-success ms-2" role="status"></div>
  </div>

  <div class="projects-table position-relative">
    <table v-if="projects.length" class="table table-striped table-hover">
      <thead>
        <tr>
          <th>uid</th>
          <th>Name</th>
          <th>Https</th>
          <th>Backend</th>
          <th>Template</th>
          <th>Backup</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in projects" :key="item.uid">
          <td>{{ item.uid }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.https }}</td>
          <td>{{ item.backend }}</td>
          <td>{{ item.template }}</td>
          <td>{{ item.backup }}</td>
          <td>
            <span class="badge" :class="item.active ? 'text-bg-success' : 'text-bg-warning'">
              {{ item.active ? 'active' : 'inactive' }}
            </span>
          </td>
          <td>
            <a class="btn btn-primary btn-sm" :href="'/admin/project/' + item.uid">Edit</a>
            <button class="btn btn-danger btn-sm" type="button" @click="onDelete(item.uid)">Delete</button>
            <button
              v-if="item.active == false"
              class="btn btn-success btn-sm"
              type="button"
              @click="onActivate(item.uid)"
            >
              Activate
            </button>
            <button
              v-if="item.active"
              class="btn btn-secondary btn-sm"
              type="button"
              @click="onDeactivate(item.uid)"
            >
              Deactivate
            </button>
            <button
              v-if="!item.actual"
              class="btn btn-warning btn-sm"
              type="button"
              @click="onApply(item)"
            >
              Apply
              <span v-if="item.applying" class="spinner-border spinner-border-sm ms-1"></span>
            </button>
            <button class="btn btn-info btn-sm" type="button" @click="onRestart(item)">
              Restart
              <span v-if="item.applying" class="spinner-border spinner-border-sm ms-1"></span>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="busy" class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="background: rgba(255,255,255,.75); z-index: 10;">
      <div v-if="processing" class="text-center p-4 bg-primary text-light rounded">
        <div class="mb-3">Processing...</div>
        <div class="progress" style="height: 3px; min-width: 240px;">
          <div class="progress-bar bg-success" :style="{ width: (counter * 5) + '%' }"></div>
        </div>
      </div>
      <div v-else class="text-center p-3 bg-white border rounded shadow-sm">
        <p><strong>Are you sure?</strong></p>
        <div class="d-flex">
          <button type="button" class="btn btn-outline-danger me-3" @click="onCancel">Cancel</button>
          <button type="button" class="btn btn-outline-success" @click="onOK">OK</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue'

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
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then((response) => {
    const data = response.data
    if (data && data.result === 'ok' && data.projects) {
      projects.value = data.projects
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
