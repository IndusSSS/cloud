<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center sm:justify-between">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Live Monitoring</h1>
        <p class="mt-2 text-sm text-gray-700">
          Real-time sensor data for {{ device?.name || 'Device' }}
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-4">
        <router-link
          :to="`/devices/${deviceId}/history`"
          class="btn-secondary"
        >
          View History
        </router-link>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="mt-8">
      <div class="card">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div
              :class="[
                'w-3 h-3 rounded-full mr-3',
                isConnected ? 'bg-green-400' : 'bg-red-400'
              ]"
            ></div>
            <span class="text-sm font-medium text-gray-900">
              {{ isConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
          <div class="text-sm text-gray-500">
            Last update: {{ lastUpdate }}
          </div>
        </div>
      </div>
    </div>

    <!-- Current Values -->
    <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Temperature</dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ latestData?.temp ? `${latestData.temp}°C` : 'N/A' }}
              </dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Humidity</dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ latestData?.humidity ? `${latestData.humidity}%` : 'N/A' }}
              </dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Data Points</dt>
              <dd class="text-lg font-medium text-gray-900">{{ sensorStore.liveData.length }}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <!-- Temperature Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Temperature Trend</h3>
        <div v-if="temperatureData.length === 0" class="text-center py-8 text-gray-500">
          No temperature data available
        </div>
        <div v-else class="h-64">
          <apexchart
            type="line"
            :options="temperatureChartOptions"
            :series="temperatureSeries"
          />
        </div>
      </div>

      <!-- Humidity Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Humidity Trend</h3>
        <div v-if="humidityData.length === 0" class="text-center py-8 text-gray-500">
          No humidity data available
        </div>
        <div v-else class="h-64">
          <apexchart
            type="line"
            :options="humidityChartOptions"
            :series="humiditySeries"
          />
        </div>
      </div>
    </div>

    <!-- Raw Data -->
    <div class="mt-8">
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Latest Data</h3>
        <div v-if="sensorStore.liveData.length === 0" class="text-center py-8 text-gray-500">
          No data received yet
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Temperature
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Humidity
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Raw Data
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(data, index) in sensorStore.liveData.slice(-10).reverse()" :key="index">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ new Date(data.timestamp).toLocaleTimeString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ data.temp ? `${data.temp}°C` : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ data.humidity ? `${data.humidity}%` : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <code class="text-xs">{{ JSON.stringify(data) }}</code>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDeviceStore } from '../stores/devices'
import { useSensorStore } from '../stores/sensor'
import { useAuthStore } from '../stores/auth'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()
const deviceStore = useDeviceStore()
const sensorStore = useSensorStore()
const authStore = useAuthStore()

const deviceId = route.params.id
const device = computed(() => deviceStore.getDeviceById(deviceId))

const isConnected = ref(false)
const lastUpdate = ref('Never')
const ws = ref(null)

const latestData = computed(() => sensorStore.getLatestData())

const temperatureData = computed(() => sensorStore.getTemperatureData())
const humidityData = computed(() => sensorStore.getHumidityData())

const temperatureSeries = computed(() => [{
  name: 'Temperature',
  data: temperatureData.value
}])

const humiditySeries = computed(() => [{
  name: 'Humidity',
  data: humidityData.value
}])

const chartOptions = {
  chart: {
    type: 'line',
    animations: {
      enabled: true,
      easing: 'linear',
      dynamicAnimation: {
        speed: 1000
      }
    },
    toolbar: {
      show: false
    }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  xaxis: {
    type: 'datetime'
  },
  yaxis: {
    labels: {
      formatter: function(val) {
        return val.toFixed(1)
      }
    }
  },
  tooltip: {
    x: {
      format: 'HH:mm:ss'
    }
  }
}

const temperatureChartOptions = computed(() => ({
  ...chartOptions,
  colors: ['#ef4444'],
  title: {
    text: 'Temperature (°C)',
    align: 'left'
  }
}))

const humidityChartOptions = computed(() => ({
  ...chartOptions,
  colors: ['#3b82f6'],
  title: {
    text: 'Humidity (%)',
    align: 'left'
  }
}))

const connectWebSocket = () => {
  const token = authStore.token
  if (!token) return

  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/live/${deviceId}?token=${token}`
  
  ws.value = new WebSocket(wsUrl)
  
  ws.value.onopen = () => {
    isConnected.value = true
    console.log('WebSocket connected')
  }
  
  ws.value.onmessage = (event) => {
    sensorStore.pushLiveData(event.data)
    lastUpdate.value = new Date().toLocaleTimeString()
  }
  
  ws.value.onclose = () => {
    isConnected.value = false
    console.log('WebSocket disconnected')
    // Reconnect after 5 seconds
    setTimeout(connectWebSocket, 5000)
  }
  
  ws.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    isConnected.value = false
  }
}

onMounted(async () => {
  await deviceStore.fetchDevices()
  sensorStore.clearLiveData()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script> 