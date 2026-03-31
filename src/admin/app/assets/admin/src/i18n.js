import { createI18n } from 'vue-i18n'
import en from './locales/en.js'
import ru from './locales/ru.js'
import zh from './locales/zh.js'

const savedLocale = localStorage.getItem('locale')
const browserLocale = navigator.language?.split('-')[0]
const locale = savedLocale || (browserLocale === 'ru' ? 'ru' : browserLocale === 'zh' ? 'zh' : 'en')

export const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: 'en',
  messages: { en, ru, zh },
})
