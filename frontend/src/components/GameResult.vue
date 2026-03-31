<script setup lang="ts">
defineProps<{
  result: {
    winner: number | null;
    win_type: string;
    fan: number;
    patterns: string[];
  } | null;
}>();
</script>

<template>
  <section v-if="result" class="result">
    <h3>本局结算</h3>
    <p>赢家: {{ result.winner === null ? "流局" : `Seat ${result.winner}` }}</p>
    <p>类型: {{ result.win_type }}</p>
    <p>番数: {{ result.fan }}</p>
    <p>番型: {{ result.patterns.join(", ") }}</p>
  </section>
</template>

<style scoped>
.result {
  border: 1px solid #866c35;
  background: #fff4d3;
  border-radius: 8px;
  padding: 10px;
}
</style>

