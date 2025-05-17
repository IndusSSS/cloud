<template>
  <div class="min-h-screen bg-gray-100 p-4">
    <h1 class="text-3xl font-bold mb-6">Admin Dashboard</h1>

    <div v-if="error" class="text-red-600 mb-4">
      {{ error }}
    </div>

    <table v-else class="w-full bg-white shadow rounded">
      <thead class="bg-gray-200">
        <tr>
          <th class="px-4 py-2 text-left">Client</th>
          <th class="px-4 py-2 text-left">Device</th>
          <th class="px-4 py-2 text-left">Metric</th>
          <th class="px-4 py-2 text-left">Value</th>
          <th class="px-4 py-2 text-left">Timestamp</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.id"
          class="border-t hover:bg-gray-50"
        >
          <td class="px-4 py-2">{{ row.client_id }}</td>
          <td class="px-4 py-2">{{ row.device_id }}</td>
          <td class="px-4 py-2">{{ row.metric }}</td>
          <td class="px-4 py-2">{{ row.value }}</td>
          <td class="px-4 py-2">{{ formatTimestamp(row.ts) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// reactive state
const rows = ref([])
const error = ref('')

// helper to format ISO timestamp strings
function formatTimestamp(ts) {
  try {
    return new Date(ts).toLocaleString()
  } catch {
    return ts
  }
}

onMounted(async () => {
  // 1) initial REST fetch
  try {
    const res = await fetch('/api/v1/telemetry?page=1&page_size=20')
    if (!res.ok) throw new Error('API error')
    const json = await res.json()
    rows.value = json.data
  } catch {
    error.value = 'Failed to load initial data'
  }

  // 2) WebSocket for live updates
  try {
    const socket = new WebSocket('wss://admin.smartsecurity.solutions/ws')
    socket.onmessage = ({ data }) => {
      const msg = JSON.parse(data)
      rows.value.unshift(msg)
      // keep only the latest 20 entries
      if (rows.value.length > 20) {
        rows.value.pop()
      }
    }
    socket.onerror = () => {
      console.error('WebSocket error')
    }
  } catch {
    console.warn('Could not open WebSocket')
  }
})
</script>

<style>
/* Add any additional custom styles here */
</style>
