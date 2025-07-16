<template>
  <div id="app">
    <LoginForm v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    
    <div v-else class="min-h-screen bg-gray-100">
      <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center">
              <h1 class="text-xl font-semibold text-gray-900">SmartSecurity Dashboard</h1>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-gray-700">Welcome, {{ username }}</span>
              <button 
                @click="logout" 
                class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Devices />
      </main>
    </div>
  </div>
</template>

<script>
import Devices from './components/Devices.vue'
import LoginForm from './components/LoginForm.vue'

export default {
  name: 'App',
  components: {
    Devices,
    LoginForm
  },
  data() {
    return {
      isLoggedIn: false,
      username: ''
    }
  },
  mounted() {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      try {
        const userData = JSON.parse(user)
        this.username = userData.username
        this.isLoggedIn = true
      } catch (e) {
        this.logout()
      }
    }
  },
  methods: {
    handleLoginSuccess(data) {
      this.username = data.username
      this.isLoggedIn = true
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.isLoggedIn = false
      this.username = ''
    }
  }
}
</script> 