<script setup lang="ts">
defineProps<{
  tile: string;
  clickable?: boolean;
}>();
</script>

<template>
  <button class="tile-card" :class="{ clickable }">
    {{ tile }}
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
</style>

