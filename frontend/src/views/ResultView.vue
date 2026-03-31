<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useGameStore } from "../stores/game";

const router = useRouter();
const store = useGameStore();
const result = computed(() => store.snapshot?.result);
</script>

<template>
  <main class="result-page">
    <section class="card" v-if="result">
      <h1>结算</h1>
      <p>赢家: {{ result.winner === null ? "流局" : `Seat ${result.winner}` }}</p>
      <p>胡牌类型: {{ result.win_type }}</p>
      <p>番数: {{ result.fan }}</p>
      <p>番型: {{ result.patterns.join(", ") }}</p>
      <button @click="router.push('/')">返回首页</button>
    </section>
    <section class="card" v-else>
      <p>暂无结算信息</p>
      <button @click="router.push('/')">返回首页</button>
    </section>
  </main>
</template>

<style scoped>
.result-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(165deg, #ece6cf, #6e9462);
}

.card {
  background: #fff7df;
  border-radius: 10px;
  padding: 20px;
  min-width: 300px;
}

button {
  margin-top: 10px;
  border: 0;
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
  background: #2f6a2a;
  color: #fff;
}
</style>

