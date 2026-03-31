import { ref } from 'vue'

// Apply immediately on module load to prevent flash
const saved = localStorage.getItem('theme') || 'light'
document.documentElement.setAttribute('data-theme', saved)
const _theme = ref(saved)

export function useTheme() {
  function toggleTheme() {
    _theme.value = _theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', _theme.value)
    document.documentElement.setAttribute('data-theme', _theme.value)
  }
  return { theme: _theme, toggleTheme }
}
