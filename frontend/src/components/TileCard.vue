<script setup lang="ts">
import { tileToLabel } from "../utils/tile";

defineProps<{
  tile: string;
  clickable?: boolean;
  enabled?: boolean;
}>();
</script>

<template>
  <button class="tile-card" :class="{ clickable, disabled: clickable && enabled === false }">
    {{ tileToLabel(tile) }}
  </button>
</template>

<style scoped>
.tile-card {
  width: 42px;
  height: 56px;
  border: 1px solid #b28b43;
  border-radius: 6px;
  background: #fff8e6;
  color: #222;
  font-weight: 700;
}

.tile-card.clickable {
  cursor: pointer;
}

.tile-card.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
