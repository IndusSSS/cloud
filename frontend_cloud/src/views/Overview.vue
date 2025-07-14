<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Dashboard Overview</h1>
        <p class="mt-2 text-sm text-gray-700">
          Welcome back, {{ authStore.user?.username }}! Here's what's happening with your devices.
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Online Devices</dt>
              <dd class="text-lg font-medium text-gray-900">{{ onlineDevicesCount }}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Devices</dt>
              <dd class="text-lg font-medium text-gray-900">{{ totalDevicesCount }}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Alerts Today</dt>
              <dd class="text-lg font-medium text-gray-900">{{ alertsToday }}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="mt-8">
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Device Activity</h3>
        <div v-if="deviceStore.loading" class="text-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else-if="deviceStore.devices.length === 0" class="text-center py-8 text-gray-500">
          No devices found. Contact support to add your first device.
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="device in deviceStore.devices.slice(0, 5)"
            :key="device.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-gray-300 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-900">{{ device.name }}</div>
                <div class="text-sm text-gray-500">{{ device.description || 'No description' }}</div>
              </div>
            </div>
            <div class="flex items-center space-x-2">
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
              <router-link
                :to="`/devices/${device.id}/live`"
                class="text-primary-600 hover:text-primary-500 text-sm font-medium"
              >
                View Live
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useDeviceStore } from '../stores/devices'

const authStore = useAuthStore()
const deviceStore = useDeviceStore()

const alertsToday = ref(0) // Placeholder for now

const totalDevicesCount = computed(() => deviceStore.devices.length)
const onlineDevicesCount = computed(() => deviceStore.getOnlineDevices().length)

onMounted(async () => {
  await deviceStore.fetchDevices()
})
</script> 