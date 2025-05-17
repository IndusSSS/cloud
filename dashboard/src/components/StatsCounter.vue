<template>
  <div class="stat-card">
    <h3>{{ label }}</h3>
    <p>{{ value }}</p>
  </div>
</template>

<script setup>
defineProps({ label: String, value: Number })
</script>

<style scoped>
.stat-card {
  background: var(--card-bg, #1e1e2f);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  color: #fff;
}
h3 { margin: 0 0 .5rem 0; font-size: 1rem; }
p  { margin: 0; font-size: 1.5rem; font-weight: bold; }
</style>
