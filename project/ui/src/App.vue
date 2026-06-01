<script setup lang="ts">
import { ref, onMounted } from 'vue';

const status = ref<string>('checking...');

onMounted(async () => {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    status.value = data.status;
  } catch {
    status.value = 'unreachable';
  }
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <p class="text-lg">API status: {{ status }}</p>
  </div>
</template>
