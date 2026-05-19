import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const userRaw = localStorage.getItem('sizzzle_user')
  const user = ref(userRaw && userRaw !== 'undefined' ? JSON.parse(userRaw) : null)
  
  const tokenRaw = localStorage.getItem('sizzzle_token')
  const token = ref(tokenRaw && tokenRaw !== 'undefined' && tokenRaw !== 'null' ? tokenRaw : null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  function setAuth(userData, authToken) {
    user.value = userData
    token.value = authToken || null
    if (userData) {
      localStorage.setItem('sizzzle_user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('sizzzle_user')
    }
    
    if (authToken) {
      localStorage.setItem('sizzzle_token', authToken)
    } else {
      localStorage.removeItem('sizzzle_token')
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('sizzzle_user')
    localStorage.removeItem('sizzzle_token')
  }

  function updateUser(data) {
    user.value = { ...user.value, ...data }
    localStorage.setItem('sizzzle_user', JSON.stringify(user.value))
  }

  return { user, token, isLoggedIn, userRole, setAuth, logout, updateUser }
})
