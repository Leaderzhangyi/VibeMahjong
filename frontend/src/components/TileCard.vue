<script setup lang="ts">
import { computed } from "vue";
import { tileToImage, tileToLabel } from "../utils/tile";

const props = defineProps<{
  tile: string;
  clickable?: boolean;
  enabled?: boolean;
}>();

const imageSrc = computed(() => tileToImage(props.tile));
</script>

<template>
  <button class="tile-card" :class="{ clickable, disabled: clickable && enabled === false }">
    <img
      v-if="imageSrc"
      class="tile-image"
      :src="imageSrc"
      :alt="tileToLabel(tile)"
      draggable="false"
    />
    <span v-else>{{ tileToLabel(tile) }}</span>
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
  padding: 0;
  overflow: hidden;
}

.tile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.tile-card.clickable {
  cursor: pointer;
}

.tile-card.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
