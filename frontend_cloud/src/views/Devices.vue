<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Devices</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage and monitor your IoT devices
        </p>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="mt-8 flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div class="flex-1 max-w-lg">
        <label for="search" class="sr-only">Search devices</label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            class="input-field pl-10"
            placeholder="Search devices..."
          />
        </div>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-4">
        <select v-model="statusFilter" class="input-field">
          <option value="">All Status</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
      </div>
    </div>

    <!-- Devices Table -->
    <div class="mt-8 card">
      <div v-if="deviceStore.loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-2 text-sm text-gray-500">Loading devices...</p>
      </div>
      
      <div v-else-if="deviceStore.error" class="text-center py-8">
        <div class="text-red-600 text-sm">{{ deviceStore.error }}</div>
        <button
          @click="deviceStore.fetchDevices()"
          class="mt-2 btn-primary"
        >
          Retry
        </button>
      </div>
      
      <div v-else-if="filteredDevices.length === 0" class="text-center py-8">
        <div class="text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No devices found</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ searchQuery || statusFilter ? 'Try adjusting your search or filter criteria.' : 'Get started by adding your first device.' }}
          </p>
        </div>
      </div>
      
      <div v-else class="overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Device
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Activity
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="device in filteredDevices" :key="device.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-gray-300 flex items-center justify-center">
                      <svg class="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ device.name }}</div>
                    <div class="text-sm text-gray-500">{{ device.description || 'No description' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    device.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ device.is_active ? 'Online' : 'Offline' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ device.is_active ? 'Active now' : 'Unknown' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <router-link
                    :to="`/devices/${device.id}/live`"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    Live
                  </router-link>
                  <router-link
                    :to="`/devices/${device.id}/history`"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    History
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDeviceStore } from '../stores/devices'

const deviceStore = useDeviceStore()

const searchQuery = ref('')
const statusFilter = ref('')

const filteredDevices = computed(() => {
  let devices = deviceStore.devices

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    devices = devices.filter(device =>
      device.name.toLowerCase().includes(query) ||
      (device.description && device.description.toLowerCase().includes(query))
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    devices = devices.filter(device => {
      if (statusFilter.value === 'online') return device.is_active
      if (statusFilter.value === 'offline') return !device.is_active
      return true
    })
  }

  return devices
})

onMounted(async () => {
  await deviceStore.fetchDevices()
})
</script> 