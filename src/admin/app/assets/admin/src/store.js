import { reactive } from 'vue'

export const store = reactive({
  user: window.user || '',
  actual: true
})
