<template>
<div class="admin-page">
  <div class="page-header">
    <h1>{{ t('admin.title') }}</h1>
  </div>
  <div class="app-card" style="max-width: 480px;">
    <ul class="versions-list">
      <li
        v-for="item in soft"
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

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const soft = window.soft || []
</script>
