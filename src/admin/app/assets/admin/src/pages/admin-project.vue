<template>
<div class="modules-editor">
  <!-- Active modules list -->
  <div v-if="modules.length" class="modules-list mb-3">
    <div
      v-for="(mod, idx) in modules"
      :key="mod._id"
      class="module-card"
      :class="'module-card--' + mod.type"
    >
      <div class="module-card-header">
        <span class="module-badge" :class="'badge-' + categoryOf(mod)">
          {{ categoryLabel(categoryOf(mod)) }}
        </span>
        <span class="module-label">{{ labelOf(mod) }}</span>
        <div class="module-card-actions">
          <button
            v-if="mod.type === 'custom'"
            type="button"
            class="btn btn-xs btn-outline-secondary"
            @click="editCustomModule(idx)"
          ><i class="bi bi-pencil"></i></button>
          <button
            type="button"
            class="btn btn-xs btn-outline-danger"
            @click="removeModule(idx)"
          ><i class="bi bi-trash"></i></button>
        </div>
      </div>

      <!-- Custom module detail preview -->
      <div v-if="mod.type === 'custom'" class="module-detail">
        <code class="module-image">{{ mod.image }}</code>
        <div v-if="mod.volumes && mod.volumes.length" class="module-volumes">
          <span v-for="(v, vi) in mod.volumes" :key="vi" class="module-volume-tag">
            {{ v.host }} → {{ v.container }}
          </span>
        </div>
        <div v-if="mod.env && Object.keys(mod.env).length" class="module-envs">
          <span v-for="(val, key) in mod.env" :key="key" class="module-env-tag">
            {{ key }}={{ val }}
          </span>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="modules-empty mb-3">
    {{ t('modules.empty') }}
  </div>

  <!-- Add module buttons — one dropdown per category -->
  <div class="modules-add-row">
    <div v-for="cat in categoriesInOrder" :key="cat" class="dropdown">
      <button
        type="button"
        class="btn btn-sm btn-outline-primary dropdown-toggle"
        data-bs-toggle="dropdown"
        :disabled="loadingPresets"
      >
        <span v-if="loadingPresets" class="spinner-border spinner-border-sm me-1"></span>
        <i v-else class="bi bi-plus-lg me-1"></i>{{ categoryLabel(cat) }}
      </button>
      <ul class="dropdown-menu">
        <li v-for="p in presetsByCategory(cat)" :key="p.preset">
          <button
            type="button"
            class="dropdown-item"
            :disabled="isPresetActive(p)"
            @click="addPreset(p)"
          >{{ p.label }}</button>
        </li>
        <li v-if="!presetsByCategory(cat).length">
          <span class="dropdown-item-text text-muted fst-italic px-3">{{ t('modules.noPresets') }}</span>
        </li>
      </ul>
    </div>
    <button
      type="button"
      class="btn btn-sm btn-outline-secondary"
      @click="openCustomDialog"
    >
      <i class="bi bi-box me-1"></i>{{ t('modules.addCustom') }}
    </button>
  </div>

  <!-- Custom module dialog -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showCustomDialog" class="dialog-backdrop" @click.self="closeCustomDialog">
        <div class="dialog" style="max-width:560px;width:100%">
          <div class="dialog-header">
            <h2>{{ editingIndex !== null ? t('modules.editCustom') : t('modules.addCustom') }}</h2>
            <button class="dialog-close" type="button" @click="closeCustomDialog">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <div class="dialog-body">
            <!-- Name -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customName') }} <span class="text-danger">*</span></label>
              <input v-model="customForm.name" type="text" class="form-control" :class="{'is-invalid': customErrors.name}" placeholder="e.g. worker">
              <div v-if="customErrors.name" class="invalid-feedback">{{ customErrors.name }}</div>
              <div class="form-text">{{ t('modules.customNameHelp') }}</div>
            </div>
            <!-- Image -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customImage') }} <span class="text-danger">*</span></label>
              <input v-model="customForm.image" type="text" class="form-control" :class="{'is-invalid': customErrors.image}" placeholder="e.g. redis:7 or myregistry.com/app:latest">
              <div v-if="customErrors.image" class="invalid-feedback">{{ customErrors.image }}</div>
            </div>
            <!-- Command -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customCommand') }}</label>
              <input v-model="customForm.command" type="text" class="form-control" placeholder="e.g. ./start.sh">
              <div class="form-text">{{ t('modules.customCommandHelp') }}</div>
            </div>
            <!-- Restart policy -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customRestart') }}</label>
              <select v-model="customForm.restart" class="form-select">
                <option value="unless-stopped">unless-stopped</option>
                <option value="always">always</option>
                <option value="on-failure">on-failure</option>
                <option value="no">no</option>
              </select>
            </div>
            <!-- Environment variables -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customEnv') }}</label>
              <div v-for="(envRow, ei) in customForm.envRows" :key="ei" class="d-flex gap-2 mb-1">
                <input v-model="envRow.key" type="text" class="form-control form-control-sm" placeholder="KEY">
                <input v-model="envRow.value" type="text" class="form-control form-control-sm" placeholder="value">
                <button type="button" class="btn btn-sm btn-outline-danger" @click="removeEnvRow(ei)">
                  <i class="bi bi-dash"></i>
                </button>
              </div>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="addEnvRow">
                <i class="bi bi-plus me-1"></i>{{ t('modules.addEnv') }}
              </button>
            </div>
            <!-- Volume mounts -->
            <div class="mb-3">
              <label class="form-label">{{ t('modules.customVolumes') }}</label>
              <div v-for="(volRow, vi) in customForm.volRows" :key="vi" class="d-flex gap-2 mb-1 align-items-center">
                <input v-model="volRow.host" type="text" class="form-control form-control-sm" placeholder="relative/host/path">
                <span class="text-muted">→</span>
                <input v-model="volRow.container" type="text" class="form-control form-control-sm" placeholder="/container/path">
                <button type="button" class="btn btn-sm btn-outline-danger" @click="removeVolRow(vi)">
                  <i class="bi bi-dash"></i>
                </button>
              </div>
              <div class="form-text mb-1">{{ t('modules.customVolumesHelp') }}</div>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="addVolRow">
                <i class="bi bi-plus me-1"></i>{{ t('modules.addVolume') }}
              </button>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="closeCustomDialog">{{ t('common.cancel') }}</button>
              <button type="button" class="btn btn-sm btn-accent" @click="saveCustomModule">{{ t('common.save') }}</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, getCurrentInstance } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { appContext } = getCurrentInstance()
const axios = appContext.config.globalProperties.axios

// ── State ────────────────────────────────────────────────────────────────────
const presets = ref([])
const loadingPresets = ref(true)
const modules = ref([])
const showCustomDialog = ref(false)
const editingIndex = ref(null)

const categoriesInOrder = ['backend', 'database', 'cache', 'search']

const emptyCustomForm = () => ({
  name: '',
  image: '',
  command: '',
  restart: 'unless-stopped',
  envRows: [],
  volRows: [],
})
const customForm = ref(emptyCustomForm())
const customErrors = ref({})

let _idCounter = 0
function nextId() { return ++_idCounter }

// ── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(async () => {
  // Load presets from API
  try {
    const resp = await axios.get('/admin/api/module-presets')
    presets.value = resp.data || []
  } catch (e) {
    console.error('Failed to load module presets', e)
  } finally {
    loadingPresets.value = false
  }

  // Initialise modules from server-rendered data
  const initial = window.__modulesData__ || []
  modules.value = initial.map(m => ({ ...m, _id: nextId() }))

  syncHiddenField()
})

// Sync to hidden field whenever modules change
watch(modules, syncHiddenField, { deep: true })

// ── Helpers ──────────────────────────────────────────────────────────────────
const CATEGORY_LABELS = {
  backend:  () => t('modules.categoryBackend'),
  database: () => t('modules.categoryDatabase'),
  cache:    () => t('modules.categoryCache'),
  search:   () => t('modules.categorySearch'),
  custom:   () => t('modules.categoryCustom'),
}

const BUILTIN_LABELS = {
  mysql:      'MySQL (MariaDB 10)',
  mysql5:     'MySQL 5 (MariaDB 5)',
  postgresql: 'PostgreSQL 12',
  memcached:  'Memcached',
  solr:       'Apache Solr 6',
  elastic:    'Elasticsearch 7',
}

const TYPE_CATEGORY = {
  core:       'backend',
  mysql:      'database',
  mysql5:     'database',
  postgresql: 'database',
  memcached:  'cache',
  solr:       'search',
  elastic:    'search',
  custom:     'custom',
}

function categoryOf(mod) {
  return TYPE_CATEGORY[mod.type] || 'custom'
}

function categoryLabel(cat) {
  return CATEGORY_LABELS[cat]?.() || cat
}

function labelOf(mod) {
  if (mod.type === 'core') {
    if (mod.label) return mod.label
    const p = presets.value.find(p => p.preset === mod.preset)
    return p?.label || mod.preset || 'Core'
  }
  if (mod.type === 'custom') return mod.name || mod.image || 'Custom'
  return BUILTIN_LABELS[mod.type] || mod.type
}

function presetsByCategory(cat) {
  return presets.value
    .filter(p => p.category === cat)
    .sort((a, b) => (a.label || '').localeCompare(b.label || ''))
}

// True when any backend (core) module is already in the list
const hasBackend = computed(() => modules.value.some(m => m.type === 'core'))


function isPresetActive(preset) {
  if (preset.type === 'core') {
    // Only one backend allowed — any active backend blocks all backend presets
    return hasBackend.value
  }
  return modules.value.some(m => m.type === preset.type)
}

// ── Actions ──────────────────────────────────────────────────────────────────
function addPreset(preset) {
  if (isPresetActive(preset)) return
  modules.value.push({
    _id:    nextId(),
    type:   preset.type,
    preset: preset.preset,
    label:  preset.label,
  })
}

function removeModule(idx) {
  modules.value.splice(idx, 1)
}

function openCustomDialog() {
  editingIndex.value = null
  customForm.value = emptyCustomForm()
  customErrors.value = {}
  showCustomDialog.value = true
}

function editCustomModule(idx) {
  const mod = modules.value[idx]
  editingIndex.value = idx
  customErrors.value = {}
  customForm.value = {
    name:    mod.name    || '',
    image:   mod.image   || '',
    command: mod.command || '',
    restart: mod.restart || 'unless-stopped',
    envRows: Object.entries(mod.env || {}).map(([key, value]) => ({ key, value })),
    volRows: (mod.volumes || []).map(v => ({ host: v.host, container: v.container })),
  }
  showCustomDialog.value = true
}

function closeCustomDialog() {
  showCustomDialog.value = false
  editingIndex.value = null
}

function validateCustomForm() {
  const errs = {}
  if (!customForm.value.name.trim()) {
    errs.name = t('modules.errorNameRequired')
  } else if (!/^[a-z][a-z0-9-]*$/.test(customForm.value.name.trim())) {
    errs.name = t('modules.errorNameInvalid')
  }
  if (!customForm.value.image.trim()) {
    errs.image = t('modules.errorImageRequired')
  }
  return errs
}

function saveCustomModule() {
  const errs = validateCustomForm()
  if (Object.keys(errs).length) {
    customErrors.value = errs
    return
  }

  const env = {}
  customForm.value.envRows.forEach(({ key, value }) => {
    if (key.trim()) env[key.trim()] = value
  })
  const volumes = customForm.value.volRows
    .filter(v => v.host.trim() && v.container.trim())
    .map(v => ({ host: v.host.trim(), container: v.container.trim() }))

  const mod = {
    type:    'custom',
    name:    customForm.value.name.trim(),
    image:   customForm.value.image.trim(),
    command: customForm.value.command.trim(),
    restart: customForm.value.restart,
    env,
    volumes,
  }

  if (editingIndex.value !== null) {
    const id = modules.value[editingIndex.value]._id
    modules.value[editingIndex.value] = { ...mod, _id: id }
  } else {
    modules.value.push({ ...mod, _id: nextId() })
  }

  closeCustomDialog()
}

function addEnvRow() { customForm.value.envRows.push({ key: '', value: '' }) }
function removeEnvRow(i) { customForm.value.envRows.splice(i, 1) }
function addVolRow() { customForm.value.volRows.push({ host: '', container: '' }) }
function removeVolRow(i) { customForm.value.volRows.splice(i, 1) }

function syncHiddenField() {
  const input = document.getElementById('modules_json_input')
  if (!input) return
  const payload = modules.value.map(({ _id, label, ...rest }) => rest)
  input.value = JSON.stringify(payload)
  input.dispatchEvent(new CustomEvent('modules-updated', { bubbles: true, detail: { modules: payload } }))
  // Also sync individual Symfony form fields for built-in modules so
  // server-side validation still sees consistent data
  syncLegacyFormFields()
}

function syncLegacyFormFields() {
  const flags = {
    project_backend:   null,
    project_mysql:     false,
    project_mysql5:    false,
    project_postgre:   false,
    project_Memcached: false,
    project_Solr:      false,
    project_Elastic:   false,
  }
  modules.value.forEach(mod => {
    switch (mod.type) {
      case 'core': {
        const sel = document.getElementById('project_backend')
        if (sel) {
          // Find option whose text matches the preset label or whose value matches
          for (const opt of sel.options) {
            const pName = mod.preset || ''
            if (opt.text.toLowerCase().includes(pName.replace('php', 'php - ').replace('gunicorn', 'gunicorn'))) {
              sel.value = opt.value
              break
            }
          }
        }
        break
      }
      case 'mysql':      setCheckbox('project_mysql', true);     break
      case 'mysql5':     setCheckbox('project_mysql5', true);    break
      case 'postgresql': setCheckbox('project_postgre', true);   break
      case 'memcached':  setCheckbox('project_Memcached', true); break
      case 'solr':       setCheckbox('project_Solr', true);      break
      case 'elastic':    setCheckbox('project_Elastic', true);   break
    }
  })
}

function setCheckbox(id, value) {
  const el = document.getElementById(id)
  if (el) el.checked = value
}
</script>

<style scoped>
.modules-editor {
  padding-top: 4px;
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-card {
  border: 1px solid var(--app-card-border);
  border-radius: 6px;
  padding: 10px 12px;
  background: var(--app-table-head-bg);
}

.module-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.badge-backend  { background: #e0edff; color: #1a56db; }
.badge-database { background: #def7ec; color: #057a55; }
.badge-cache    { background: #fdf6b2; color: #92400e; }
.badge-search   { background: #ede9fe; color: #6d28d9; }
.badge-custom   { background: #f3f4f6; color: #374151; }

.module-label {
  font-weight: 500;
  font-size: 0.9rem;
  color: var(--app-text);
  flex: 1;
}

.module-card-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.btn-xs {
  padding: 2px 6px;
  font-size: 0.75rem;
  line-height: 1.4;
}

.module-detail {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.module-image {
  font-size: 0.8rem;
  background: var(--app-bg);
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid var(--app-card-border);
  color: var(--app-text-secondary);
}

.module-volume-tag,
.module-env-tag {
  font-size: 0.75rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--app-border-strong);
  color: var(--app-text-secondary);
  font-family: monospace;
}

.modules-empty {
  color: var(--app-text-muted);
  font-size: 0.9rem;
  padding: 8px 0;
}

.modules-add-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dropdown-menu {
  max-height: 360px;
  overflow-y: auto;
}
</style>
