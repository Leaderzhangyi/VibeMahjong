<script setup lang="ts">
import type { PlayerView } from "../types/game";

defineProps<{
  players: PlayerView[];
  currentTurn: number | null;
}>();
</script>

<template>
  <div class="scores">
    <div
      v-for="p in players"
      :key="p.seat"
      class="player"
      :class="{ active: currentTurn === p.seat }"
    >
      <strong>{{ p.name || `玩家${p.seat}` }}</strong>
      <span>Seat {{ p.seat }}</span>
      <span>分数 {{ p.score }}</span>
      <span>定缺 {{ p.lack || "-" }}</span>
    </div>
  </div>
</template>

<style scoped>
.scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}

.player {
  background: #f1efe4;
  border-radius: 8px;
  padding: 8px;
  border: 1px solid #d4ccb7;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.player.active {
  border-color: #37743d;
  box-shadow: 0 0 0 2px rgba(55, 116, 61, 0.2) inset;
}
</style>

