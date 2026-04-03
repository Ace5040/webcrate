<template>
<div class="admin-page">
  <div class="page-header">
    <h1>{{ t('admin.title') }}</h1>
  </div>
  <div class="app-card versions-tabs-card" style="max-width: 480px;">
    <div v-if="loading" class="versions-loading">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      <span>{{ t('common.loading') }}</span>
    </div>
    <template v-else-if="Object.keys(soft).length">
      <ul class="nav nav-tabs versions-tabs" role="tablist">
        <li
          v-for="container in Object.keys(soft)"
          :key="container"
          class="nav-item"
          role="presentation"
        >
          <button
            class="nav-link"
            :class="{ active: activeTab === container }"
            type="button"
            role="tab"
            @click="activeTab = container"
          >{{ container }}</button>
        </li>
      </ul>
      <div class="tab-content">
        <div
          v-for="(items, container) in soft"
          :key="container"
          class="tab-pane"
          :class="{ 'show active': activeTab === container }"
          role="tabpanel"
        >
          <ul class="versions-list">
            <li
              v-for="item in items"
              :key="item.name"
              class="version-item"
            >
              <span class="version-name">{{ item.name }}</span>
              <span class="version-badge">{{ item.version ? item.version : t('admin.na') }}</span>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const soft = ref({})
const activeTab = ref(null)
const loading = ref(true)

onMounted(async () => {
  const response = await fetch('/admin/api/versions')
  const data = await response.json()
  soft.value = data
  activeTab.value = Object.keys(data)[0] ?? null
  loading.value = false
})
</script>
