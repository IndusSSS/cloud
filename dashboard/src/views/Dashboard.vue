<script setup>
import { ref, onMounted } from 'vue'
import StatsCounter from '@/components/StatsCounter.vue'
import axios from '@/utils/axios'  // adjust path if needed

const counts = ref({ devices: 0, sensors: 0, actuators: 0 })

onMounted(async () => {
  const { data } = await axios.get('/v1/metrics/')
  counts.value = data
})
</script>

<template>
  <section class="grid">
    <StatsCounter label="Devices"   :value="counts.devices"   />
    <StatsCounter label="Sensors"   :value="counts.sensors"   />
    <StatsCounter label="Actuators" :value="counts.actuators" />
  </section>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}
</style>
