import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // Configure axios defaults
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        username,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/v1/users/me')
      user.value = response.data
      return { success: true }
    } catch (error) {
      console.error('Fetch profile error:', error)
      return { success: false }
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    try {
      await axios.put('/api/v1/users/me/password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      return { success: true }
    } catch (error) {
      console.error('Change password error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Password change failed' 
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    fetchProfile,
    changePassword
  }
}) 