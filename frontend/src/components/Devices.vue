<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Device Management</h2>
      
      <!-- Device Creation -->
      <div class="mb-6">
        <h3 class="text-md font-medium text-gray-700 mb-2">Create New Device</h3>
        <div class="flex space-x-4">
          <input 
            v-model="newDeviceName" 
            placeholder="Device name" 
            class="flex-1 border border-gray-300 rounded-md px-3 py-2"
          />
          <button 
            @click="createDevice" 
            class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Create Device
          </button>
        </div>
      </div>
      
      <!-- Device List -->
      <div class="space-y-4">
        <h3 class="text-md font-medium text-gray-700">Your Devices</h3>
        <div v-for="device in devices" :key="device.id" class="border border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-center">
            <div>
              <h4 class="font-medium text-gray-900">{{ device.name }}</h4>
              <p class="text-sm text-gray-500">ID: {{ device.id }}</p>
            </div>
            <button 
              @click="selectDevice(device)" 
              class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
            >
              View Data
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Live Data Chart -->
    <div v-if="selectedDevice" class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">
        Live Data: {{ selectedDevice.name }}
      </h2>
      <div class="h-64">
        <apexchart
          type="line"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>
      <div class="mt-4 text-sm text-gray-600">
        <p>WebSocket Status: {{ wsStatus }}</p>
        <p>Last Update: {{ lastUpdate }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'
import axios from 'axios'

export default {
  name: 'Devices',
  components: {
    apexchart: VueApexCharts
  },
  data() {
    return {
      devices: [],
      newDeviceName: '',
      selectedDevice: null,
      wsConnection: null,
      wsStatus: 'Disconnected',
      lastUpdate: 'Never',
      chartData: [],
      chartOptions: {
        chart: {
          type: 'line',
          animations: {
            enabled: true,
            easing: 'linear',
            dynamicAnimation: {
              speed: 1000
            }
          }
        },
        xaxis: {
          type: 'datetime'
        },
        yaxis: {
          title: {
            text: 'Temperature (°C)'
          }
        },
        title: {
          text: 'Real-time Sensor Data'
        }
      },
      chartSeries: [{
        name: 'Temperature',
        data: []
      }]
    }
  },
  async mounted() {
    await this.loadDevices()
  },
  methods: {
    async loadDevices() {
      try {
        const response = await axios.get('/api/v1/devices')
        this.devices = response.data
      } catch (error) {
        console.error('Error loading devices:', error)
        // For demo, create a mock device
        this.devices = [{
          id: 'demo-device-123',
          name: 'Demo Device',
          description: 'Demo device for testing'
        }]
      }
    },
    
    async createDevice() {
      if (!this.newDeviceName.trim()) return
      
      try {
        const response = await axios.post('/api/v1/devices', {
          name: this.newDeviceName,
          description: 'Created via dashboard'
        })
        this.devices.push(response.data)
        this.newDeviceName = ''
      } catch (error) {
        console.error('Error creating device:', error)
        // For demo, add mock device
        this.devices.push({
          id: `device-${Date.now()}`,
          name: this.newDeviceName,
          description: 'Created via dashboard'
        })
        this.newDeviceName = ''
      }
    },
    
    selectDevice(device) {
      this.selectedDevice = device
      this.connectWebSocket(device.id)
    },
    
    connectWebSocket(deviceId) {
      if (this.wsConnection) {
        this.wsConnection.close()
      }
      
      const wsUrl = `ws://localhost:8000/api/v1/ws/live/${deviceId}`
      this.wsConnection = new WebSocket(wsUrl)
      
      this.wsConnection.onopen = () => {
        this.wsStatus = 'Connected'
        console.log('WebSocket connected')
      }
      
      this.wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.processSensorData(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.wsConnection.onclose = () => {
        this.wsStatus = 'Disconnected'
        console.log('WebSocket disconnected')
      }
      
      this.wsConnection.onerror = (error) => {
        this.wsStatus = 'Error'
        console.error('WebSocket error:', error)
      }
    },
    
    processSensorData(data) {
      const timestamp = new Date().getTime()
      const temperature = data.payload?.temp || Math.random() * 30 + 10
      
      this.chartSeries[0].data.push([timestamp, temperature])
      
      // Keep only last 20 data points
      if (this.chartSeries[0].data.length > 20) {
        this.chartSeries[0].data.shift()
      }
      
      this.lastUpdate = new Date().toLocaleTimeString()
    }
  },
  
  beforeUnmount() {
    if (this.wsConnection) {
      this.wsConnection.close()
    }
  }
}
</script> 