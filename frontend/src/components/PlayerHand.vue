<script setup lang="ts">
import TileCard from "./TileCard.vue";

const props = defineProps<{
  tiles: string[];
  clickable?: boolean;
  allowedTiles?: string[];
}>();

const emit = defineEmits<{
  (e: "select", tile: string): void;
}>();

const onClick = (tile: string) => {
  if (!props.clickable) return;
  if (props.allowedTiles && !props.allowedTiles.includes(tile)) return;
  emit("select", tile);
};
</script>

<template>
  <div class="hand">
    <TileCard
      v-for="(tile, idx) in tiles"
      :key="`${tile}-${idx}`"
      :tile="tile"
      :clickable="clickable"
      :enabled="!allowedTiles || allowedTiles.includes(tile)"
      @click="onClick(tile)"
    />
  </div>
</template>

<style scoped>
.hand {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
