<template>
<nav class="app-navbar navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="/">
      <LogoIcon :size="28" />Webcrate
    </a>
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#nav-collapse"
      aria-controls="nav-collapse"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>
    <div id="nav-collapse" class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <a class="nav-link" href="/admin/projects">{{ t('nav.projects') }}</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="/admin/redirects">{{ t('nav.redirects') }}</a>
        </li>
      </ul>
      <ul class="navbar-nav mt-2 mt-lg-0 ms-lg-auto">
        <li class="nav-item">
          <div class="d-flex align-items-center gap-2 py-1 py-lg-0">
            <div class="lang-switcher">
              <button class="lang-btn" :class="{ active: locale === 'en' }" @click="setLocale('en')">EN</button>
              <button class="lang-btn" :class="{ active: locale === 'ru' }" @click="setLocale('ru')">RU</button>
              <button class="lang-btn" :class="{ active: locale === 'zh' }" @click="setLocale('zh')">中文</button>
            </div>
            <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Light mode' : 'Dark mode'">
              <i :class="theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'"></i>
            </button>
          </div>
        </li>
        <li class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle"
            href="#"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="bi bi-person-circle me-1"></i>{{ user }}
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" href="/logout">
                <i class="bi bi-box-arrow-right me-2"></i>{{ t('nav.logout') }}
              </a>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import LogoIcon from './LogoIcon.vue'
import { useTheme } from '../composables/useTheme.js'

const { t, locale } = useI18n()
const user = window.user || ''
const { theme, toggleTheme } = useTheme()

function setLocale(lang) {
  locale.value = lang
  localStorage.setItem('locale', lang)
}
</script>
