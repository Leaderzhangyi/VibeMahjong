<script setup lang="ts">
import TileCard from "./TileCard.vue";

defineProps<{
  discards: string[];
}>();
</script>

<template>
  <div class="pool">
    <TileCard v-for="(tile, idx) in discards" :key="`${tile}-${idx}`" :tile="tile" />
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
