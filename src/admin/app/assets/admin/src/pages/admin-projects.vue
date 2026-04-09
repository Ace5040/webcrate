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
            <td>{{ item.backup ? t('common.yes') : t('common.no') }}</td>
            <td>
              <span class="status-badge" :class="item.active ? 'active' : 'inactive'">
                {{ item.active ? t('common.active') : t('common.inactive') }}
              </span>
            </td>
            <td>
              <div class="row-actions">
                <a class="btn btn-sm btn-outline-primary" :class="{ disabled: item.applying }" :href="item.applying ? null : '/admin/project/' + item.uid">
                  <i class="bi bi-pencil me-1"></i>{{ t('common.edit') }}
                </a>
                <button class="btn btn-sm btn-outline-danger" type="button" :disabled="item.applying" @click="onDelete(item.uid)">
                  <i class="bi bi-trash me-1"></i>{{ t('common.delete') }}
                </button>
                <button
                  v-if="item.active == false"
                  class="btn btn-sm btn-outline-success"
                  type="button"
                  :disabled="item.applying"
                  @click="onActivate(item.uid)"
                ><i class="bi bi-toggle-off me-1"></i>{{ t('common.activate') }}</button>
                <button
                  v-if="item.active"
                  class="btn btn-sm btn-outline-secondary"
                  type="button"
                  :disabled="item.applying"
                  @click="onDeactivate(item.uid)"
                ><i class="bi bi-toggle-on me-1"></i>{{ t('common.deactivate') }}</button>
                <button
                  v-if="!item.actual"
                  class="btn btn-sm btn-outline-warning"
                  type="button"
                  :disabled="item.applying"
                  @click="onApply(item)"
                >
                  <span class="btn-icon me-1">
                    <span v-if="item.applying" class="spinner-border spinner-border-sm"></span>
                    <i v-else class="bi bi-check2-circle"></i>
                  </span>{{ t('common.apply') }}
                </button>
                <button class="btn btn-sm btn-outline-info" type="button" :disabled="item.applying" @click="onRestart(item)">
                  <span class="btn-icon me-1">
                    <span v-if="item.applying" class="spinner-border spinner-border-sm"></span>
                    <i v-else class="bi bi-arrow-clockwise"></i>
                  </span>{{ t('projects.restart') }}
                </button>
                <button
                  v-if="item.backup"
                  class="btn btn-sm btn-outline-secondary"
                  type="button"
                  :disabled="item.applying"
                  @click="openBackupDialog(item)"
                ><i class="bi bi-archive me-1"></i>{{ t('projects.backups') }}</button>
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
<Teleport to="body">
  <Transition name="fade">
    <div v-if="showBackupDialog" class="dialog-backdrop" @click.self="closeBackupDialog">
      <div class="dialog dialog-backup" style="max-width:800px;width:100%">
        <div class="dialog-header">
          <h2>{{ t('projects.backupsFor') }} {{ backupProject?.name }}</h2>
          <button class="dialog-close" type="button" @click="closeBackupDialog">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="dialog-body dialog-body-scroll">
          <div class="mb-3 d-flex gap-2 align-items-center">
            <button class="btn btn-sm btn-outline-warning" type="button" :disabled="backupRunning || !backupProject?.backup" @click="onRunBackup">
              <span class="btn-icon me-1">
                <span v-if="backupRunning" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-play-circle"></i>
              </span>{{ t('projects.runBackup') }}
            </button>
            <button class="btn btn-sm btn-outline-secondary" type="button" :disabled="backupListLoading" @click="loadBackupList">
              <span class="btn-icon me-1">
                <span v-if="backupListLoading" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-arrow-clockwise"></i>
              </span>{{ t('common.reload') }}
            </button>
          </div>

          <div v-if="backupListLoading && backupSets.length === 0" class="text-center py-3">
            <span class="spinner-border spinner-border-sm me-2"></span>{{ t('common.loading') }}
          </div>
          <div v-else-if="!backupListLoading && backupSets.length === 0" class="text-muted py-2">
            {{ t('projects.noBackups') }}
          </div>
          <div v-else class="position-relative">
            <div v-if="backupListLoading" class="backup-list-overlay"></div>
            <table class="app-table">
              <thead>
                <tr>
                  <th>{{ t('projects.backupType') }}</th>
                  <th>{{ t('projects.backupTime') }}</th>
                  <th>{{ t('projects.backupVolumes') }}</th>
                  <th>{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="set in pagedBackupSets" :key="set.time">
                  <td>{{ set.type === 'Full' ? t('projects.backupTypeFull') : t('projects.backupTypeIncremental') }}</td>
                  <td>{{ formatBackupTime(set.time) }}</td>
                  <td>{{ set.volumes }}</td>
                  <td>
                    <div class="d-flex gap-1 align-items-center">
                      <button class="btn btn-sm btn-outline-primary" type="button" :disabled="backupSaving === set.time" @click="onSaveBackup(set.time, false)">
                        <span v-if="backupSaving === set.time" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-folder2-open me-1"></i>{{ t('projects.saveBackup') }}
                      </button>
                      <button class="btn btn-sm btn-outline-secondary" type="button" :disabled="backupSaving === set.time" @click="onSaveBackup(set.time, true)">
                        <span v-if="backupSaving === set.time" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-file-zip me-1"></i>{{ t('projects.saveBackupArchive') }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="backupTotalPages > 1" class="d-flex align-items-center justify-content-between mt-2">
              <span class="text-muted small">{{ (backupPage - 1) * BACKUP_PAGE_SIZE + 1 }}–{{ Math.min(backupPage * BACKUP_PAGE_SIZE, backupSets.length) }} / {{ backupSets.length }}</span>
              <div class="d-flex gap-1">
                <button class="btn btn-sm btn-outline-secondary" type="button" :disabled="backupPage === 1" @click="backupPage--">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary" type="button" :disabled="backupPage === backupTotalPages" @click="backupPage++">
                  <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</Teleport>
</template>

<script setup>
import { ref, computed, getCurrentInstance } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
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

const showBackupDialog = ref(false)
const backupProject = ref(null)
const backupList = ref({})
const backupSets = ref([])
const backupListLoading = ref(false)
const backupRunning = ref(false)
const backupSaving = ref(null)
const backupPage = ref(1)
const BACKUP_PAGE_SIZE = 10
const backupTotalPages = computed(() => Math.ceil(backupSets.value.length / BACKUP_PAGE_SIZE))
const pagedBackupSets = computed(() => {
  const start = (backupPage.value - 1) * BACKUP_PAGE_SIZE
  return backupSets.value.slice(start, start + BACKUP_PAGE_SIZE)
})

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

function formatBackupTime(iso) {
  if (!iso) return iso
  const d = new Date(iso)
  if (isNaN(d)) return iso
  return d.toLocaleString(locale.value, {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function openBackupDialog(item) {
  backupProject.value = item
  backupList.value = {}
  backupSets.value = []
  showBackupDialog.value = true
  loadBackupList()
}

function closeBackupDialog() {
  showBackupDialog.value = false
  backupProject.value = null
}

function loadBackupList() {
  if (!backupProject.value) return
  backupListLoading.value = true
  axios.get('/admin/project/' + backupProject.value.uid + '/backup-list')
    .then((response) => {
      const data = response.data
      if (data && data.result === 'ok') {
        backupList.value = data.backups || {}
        const sets = []
        for (const uri in backupList.value) {
          const projects = backupList.value[uri]?.projects || {}
          for (const proj in projects) {
            const files = projects[proj]?.files || []
            for (const chain of files) {
              for (const set of (chain.sets || [])) {
                sets.push(set)
              }
            }
          }
        }
        sets.sort((a, b) => b.time.localeCompare(a.time))
        backupSets.value = sets
        backupPage.value = 1
      }
      backupListLoading.value = false
    })
    .catch(() => {
      backupListLoading.value = false
    })
}

function onRunBackup() {
  if (!backupProject.value || backupRunning.value) return
  backupRunning.value = true
  axios.get('/admin/project/' + backupProject.value.uid + '/backup')
    .then(() => {
      backupRunning.value = false
      loadBackupList()
    })
    .catch(() => {
      backupRunning.value = false
    })
}

function onSaveBackup(time, archive) {
  if (!backupProject.value || backupSaving.value) return
  backupSaving.value = time
  const params = new URLSearchParams({ time, archive: archive ? 'archive' : '' })
  axios.post('/admin/project/' + backupProject.value.uid + '/backup-save', params)
    .then(() => {
      backupSaving.value = null
    })
    .catch(() => {
      backupSaving.value = null
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

<style scoped>
.backup-list-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.5);
  z-index: 1;
  border-radius: 4px;
}

.dialog-backup {
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-body-scroll {
  overflow-y: auto;
  min-height: 0;
}
</style>
