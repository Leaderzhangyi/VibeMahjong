<script setup lang="ts">
defineProps<{
  discards: string[];
}>();
</script>

<template>
  <div class="pool">
    <span v-for="(tile, idx) in discards" :key="`${tile}-${idx}`">{{ tile }}</span>
  </div>
</template>

<style scoped>
.pool {
  min-height: 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  background: #13361f;
  border-radius: 8px;
  padding: 8px;
  color: #f9f2dc;
}
</style>

