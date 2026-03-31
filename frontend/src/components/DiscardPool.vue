<script setup lang="ts">
import { tileToLabel } from "../utils/tile";

defineProps<{
  discards: string[];
}>();
</script>

<template>
  <div class="pool">
    <span v-for="(tile, idx) in discards" :key="`${tile}-${idx}`">{{ tileToLabel(tile) }}</span>
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
