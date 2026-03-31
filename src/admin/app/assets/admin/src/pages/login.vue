<template>
<div class="login-page">
  <nav class="app-navbar navbar navbar-dark">
    <div class="container-fluid">
      <a class="navbar-brand" href="/">
        <LogoIcon :size="26" />Webcrate
      </a>
      <div class="d-flex align-items-center gap-2 ms-auto">
        <div class="lang-switcher">
          <button class="lang-btn" :class="{ active: locale === 'en' }" @click="setLocale('en')">EN</button>
          <button class="lang-btn" :class="{ active: locale === 'ru' }" @click="setLocale('ru')">RU</button>
          <button class="lang-btn" :class="{ active: locale === 'zh' }" @click="setLocale('zh')">中文</button>
        </div>
        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Light mode' : 'Dark mode'">
          <i :class="theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'"></i>
        </button>
      </div>
    </div>
  </nav>
  <div class="login-body">
    <div class="login-card">
      <div class="login-logo">
        <div class="logo-icon">
          <LogoIcon :size="22" />
        </div>
        <span class="logo-text">Webcrate</span>
      </div>
      <h1>{{ t('login.title') }}</h1>

      <div v-if="error" v-html="errorMessage" class="alert alert-danger mb-3" style="font-size:.875rem; border-radius: 8px;"></div>

      <form method="post">
        <div class="mb-3">
          <label for="email" class="form-label">{{ t('login.email') }}</label>
          <input
            id="email"
            v-model="lastUsername"
            name="email"
            type="email"
            required
            placeholder="you@example.com"
            class="form-control"
          >
        </div>
        <div class="mb-4">
          <label for="password" class="form-label">{{ t('login.password') }}</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            placeholder="••••••••"
            class="form-control"
          >
        </div>
        <input name="_csrf_token" :value="csrfToken" type="hidden">
        <button type="submit" class="btn btn-login">{{ t('login.submit') }}</button>
      </form>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import LogoIcon from '../components/LogoIcon.vue'
import { useTheme } from '../composables/useTheme.js'

const { t, locale } = useI18n()
const { theme, toggleTheme } = useTheme()

const error = ref(window.error)
const errorMessage = ref(window.error_message)
const csrfToken = ref(window.csrf_token)
const lastUsername = ref(window.last_username)

function setLocale(lang) {
  locale.value = lang
  localStorage.setItem('locale', lang)
}
</script>
