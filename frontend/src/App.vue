<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">SmartSecurity Dashboard</h1>
          </div>
          <div class="flex items-center">
            <button 
              v-if="!isLoggedIn" 
              @click="login" 
              class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Login
            </button>
            <span v-else class="text-gray-700">Welcome, {{ username }}</span>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div v-if="!isLoggedIn" class="text-center py-12">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Welcome to SmartSecurity</h2>
        <p class="text-gray-600">Please login to access your devices and sensor data.</p>
      </div>
      
      <div v-else>
        <Devices />
      </div>
    </main>
  </div>
</template>

<script>
import Devices from './components/Devices.vue'

export default {
  name: 'App',
  components: {
    Devices
  },
  data() {
    return {
      isLoggedIn: false,
      username: 'admin'
    }
  },
  methods: {
    login() {
      // Simulate login for demo
      this.isLoggedIn = true
    }
  }
}
</script> 