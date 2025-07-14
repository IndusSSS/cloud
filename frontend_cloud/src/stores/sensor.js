import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useSensorStore = defineStore('sensor', () => {
  const sensorData = ref([])
  const liveData = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchSensorHistory = async (deviceId, fromTime = null, toTime = null, limit = 100) => {
    loading.value = true
    error.value = null
    
    try {
      const params = { limit }
      if (fromTime) params.from_time = fromTime
      if (toTime) params.to_time = toTime
      
      const response = await axios.get(`/api/v1/devices/${deviceId}/sensor-data`, { params })
      sensorData.value = response.data.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch sensor data'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const pushLiveData = (data) => {
    try {
      const parsedData = typeof data === 'string' ? JSON.parse(data) : data
      liveData.value.push({
        ...parsedData,
        timestamp: new Date().toISOString()
      })
      
      // Keep only last 50 data points
      if (liveData.value.length > 50) {
        liveData.value = liveData.value.slice(-50)
      }
    } catch (err) {
      console.error('Error parsing live data:', err)
    }
  }

  const clearLiveData = () => {
    liveData.value = []
  }

  const getLatestData = () => {
    return liveData.value[liveData.value.length - 1] || null
  }

  const getTemperatureData = () => {
    return liveData.value
      .filter(item => item.temp !== undefined)
      .map(item => ({
        x: new Date(item.timestamp).getTime(),
        y: item.temp
      }))
  }

  const getHumidityData = () => {
    return liveData.value
      .filter(item => item.humidity !== undefined)
      .map(item => ({
        x: new Date(item.timestamp).getTime(),
        y: item.humidity
      }))
  }

  return {
    sensorData,
    liveData,
    loading,
    error,
    fetchSensorHistory,
    pushLiveData,
    clearLiveData,
    getLatestData,
    getTemperatureData,
    getHumidityData
  }
}) 