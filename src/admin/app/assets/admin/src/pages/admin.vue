<template>
<div class="admin-page">
  <div class="page-header">
    <h1>{{ t('admin.title') }}</h1>
  </div>
  <div class="app-card versions-tabs-card" style="max-width: 480px;">
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
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const soft = window.soft || {}
const firstTab = Object.keys(soft)[0] ?? null
const activeTab = ref(firstTab)
</script>
