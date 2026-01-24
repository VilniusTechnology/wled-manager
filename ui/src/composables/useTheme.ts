import { ref, onMounted } from 'vue'
import { setCookie, getCookie } from '../utils/cookies'

export const useTheme = () => {
  const isDark = ref(false)

  const setTheme = (theme: 'light' | 'dark') => {
    isDark.value = theme === 'dark'
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    setCookie('theme', theme, 365) // Persist for 1 year
  }

  const toggleTheme = () => {
    setTheme(isDark.value ? 'light' : 'dark')
  }

  const loadTheme = () => {
    const savedTheme = getCookie('theme') as 'light' | 'dark' | null
    if (savedTheme) {
      setTheme(savedTheme)
    } else {
      setTheme('dark')
    }
  }

  onMounted(() => {
    loadTheme()
  })

  return {
    isDark,
    setTheme,
    toggleTheme,
    loadTheme
  }
}