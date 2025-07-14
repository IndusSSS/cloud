import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useDeviceStore = defineStore('devices', () => {
  const devices = ref([])
  const currentDevice = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchDevices = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('/api/v1/devices/')
      devices.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch devices'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchDevice = async (deviceId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`/api/v1/devices/${deviceId}`)
      currentDevice.value = response.data
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch device'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const getDeviceById = (deviceId) => {
    return devices.value.find(device => device.id === deviceId)
  }

  const getOnlineDevices = () => {
    return devices.value.filter(device => device.is_active)
  }

  return {
    devices,
    currentDevice,
    loading,
    error,
    fetchDevices,
    fetchDevice,
    getDeviceById,
    getOnlineDevices
  }
}) 