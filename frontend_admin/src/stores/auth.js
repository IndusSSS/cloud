import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('admin_token') || null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isSystemAdmin = computed(() => user.value?.is_admin === true)

  // Actions
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed')
      }

      // Verify user is system admin
      if (!data.user.is_admin) {
        throw new Error('Access denied. System admin privileges required.')
      }

      // Store token and user data
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('admin_token', data.access_token)

      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const validateToken = async (tokenToValidate) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${tokenToValidate}`,
        },
      })

      if (!response.ok) {
        throw new Error('Invalid token')
      }

      const data = await response.json()
      
      // Verify user is system admin
      if (!data.is_admin) {
        throw new Error('Access denied. System admin privileges required.')
      }

      user.value = data
      token.value = tokenToValidate
      return data
    } catch (err) {
      logout()
      throw err
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    error.value = null
    localStorage.removeItem('admin_token')
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isSystemAdmin,
    
    // Actions
    login,
    validateToken,
    logout,
    clearError,
  }
}) 