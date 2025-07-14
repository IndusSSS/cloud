<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center sm:justify-between">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Device History</h1>
        <p class="mt-2 text-sm text-gray-700">
          Historical sensor data for {{ device?.name || 'Device' }}
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-4">
        <router-link
          :to="`/devices/${deviceId}/live`"
          class="btn-secondary"
        >
          View Live
        </router-link>
      </div>
    </div>

    <!-- Date Range Picker -->
    <div class="mt-8 card">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div>
          <label for="from-date" class="block text-sm font-medium text-gray-700">From Date</label>
          <input
            id="from-date"
            v-model="fromDate"
            type="datetime-local"
            class="input-field mt-1"
          />
        </div>
        <div>
          <label for="to-date" class="block text-sm font-medium text-gray-700">To Date</label>
          <input
            id="to-date"
            v-model="toDate"
            type="datetime-local"
            class="input-field mt-1"
          />
        </div>
        <div>
          <label for="limit" class="block text-sm font-medium text-gray-700">Limit</label>
          <select id="limit" v-model="limit" class="input-field mt-1">
            <option value="50">50 records</option>
            <option value="100">100 records</option>
            <option value="200">200 records</option>
            <option value="500">500 records</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="fetchHistory"
            :disabled="sensorStore.loading"
            class="btn-primary w-full"
          >
            {{ sensorStore.loading ? 'Loading...' : 'Fetch Data' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div v-if="sensorStore.sensorData.length > 0" class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <!-- Temperature Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Temperature History</h3>
        <div class="h-64">
          <apexchart
            type="line"
            :options="temperatureChartOptions"
            :series="temperatureSeries"
          />
        </div>
      </div>

      <!-- Humidity Chart -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Humidity History</h3>
        <div class="h-64">
          <apexchart
            type="line"
            :options="humidityChartOptions"
            :series="humiditySeries"
          />
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="mt-8">
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Historical Data</h3>
          <div class="text-sm text-gray-500">
            {{ sensorStore.sensorData.length }} records
          </div>
        </div>
        
        <div v-if="sensorStore.loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-500">Loading data...</p>
        </div>
        
        <div v-else-if="sensorStore.sensorData.length === 0" class="text-center py-8 text-gray-500">
          No historical data found. Try adjusting the date range or fetch data.
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
              <tr v-for="data in sensorStore.sensorData" :key="data.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ new Date(data.timestamp).toLocaleString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getTemperature(data) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getHumidity(data) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <code class="text-xs">{{ data.payload }}</code>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDeviceStore } from '../stores/devices'
import { useSensorStore } from '../stores/sensor'

const route = useRoute()
const deviceStore = useDeviceStore()
const sensorStore = useSensorStore()

const deviceId = route.params.id
const device = computed(() => deviceStore.getDeviceById(deviceId))

const fromDate = ref('')
const toDate = ref('')
const limit = ref('100')

const temperatureSeries = computed(() => [{
  name: 'Temperature',
  data: sensorStore.sensorData
    .filter(data => getTemperature(data) !== 'N/A')
    .map(data => ({
      x: new Date(data.timestamp).getTime(),
      y: parseFloat(getTemperature(data).replace('°C', ''))
    }))
}])

const humiditySeries = computed(() => [{
  name: 'Humidity',
  data: sensorStore.sensorData
    .filter(data => getHumidity(data) !== 'N/A')
    .map(data => ({
      x: new Date(data.timestamp).getTime(),
      y: parseFloat(getHumidity(data).replace('%', ''))
    }))
}])

const chartOptions = {
  chart: {
    type: 'line',
    toolbar: {
      show: true
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
      format: 'dd MMM yyyy HH:mm'
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

const getTemperature = (data) => {
  try {
    const payload = JSON.parse(data.payload)
    return payload.temp ? `${payload.temp}°C` : 'N/A'
  } catch {
    return 'N/A'
  }
}

const getHumidity = (data) => {
  try {
    const payload = JSON.parse(data.payload)
    return payload.humidity ? `${payload.humidity}%` : 'N/A'
  } catch {
    return 'N/A'
  }
}

const fetchHistory = async () => {
  const params = {
    limit: parseInt(limit.value)
  }
  
  if (fromDate.value) {
    params.from_time = new Date(fromDate.value).toISOString()
  }
  
  if (toDate.value) {
    params.to_time = new Date(toDate.value).toISOString()
  }
  
  await sensorStore.fetchSensorHistory(deviceId, params.from_time, params.to_time, params.limit)
}

onMounted(async () => {
  await deviceStore.fetchDevices()
  
  // Set default date range (last 24 hours)
  const now = new Date()
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  
  fromDate.value = yesterday.toISOString().slice(0, 16)
  toDate.value = now.toISOString().slice(0, 16)
  
  await fetchHistory()
})
</script> 