<script setup lang="ts">
import { tileToLabel } from "../utils/tile";

const props = defineProps<{
  actions: string[];
  targetTile?: string;
  concealedKongTiles?: string[];
}>();

const emit = defineEmits<{
  (e: "action", action: string, payload?: Record<string, unknown>): void;
}>();

const labels: Record<string, string> = {
  pong: "碰",
  kong_exposed: "明杠",
  kong_concealed: "暗杠",
  win: "胡",
  win_self_draw: "自摸",
  pass: "过",
  discard: "出牌",
};

const doAction = (action: string) => {
  if (action === "kong_concealed") {
    const tile = props.concealedKongTiles?.[0];
    emit("action", action, tile ? { tile } : {});
    return;
  }
  emit("action", action, {});
};
</script>

<template>
  <div class="action-bar">
    <button v-for="action in actions" :key="action" class="action-btn" @click="doAction(action)">
      {{ labels[action] || action }}
      <span v-if="targetTile && ['pong', 'kong_exposed', 'win'].includes(action)">
        ({{ tileToLabel(targetTile) }})
      </span>
    </button>
  </div>
</template>

<style scoped>
.action-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 10px;
  border: 1px solid #2b5f3a;
  background: #dceeca;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
}
</style>

