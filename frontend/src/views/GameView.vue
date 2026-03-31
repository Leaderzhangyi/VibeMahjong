<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import ActionBar from "../components/ActionBar.vue";
import DiscardPool from "../components/DiscardPool.vue";
import GameResult from "../components/GameResult.vue";
import PlayerHand from "../components/PlayerHand.vue";
import ScoreBoard from "../components/ScoreBoard.vue";
import { useGameStore } from "../stores/game";

const route = useRoute();
const router = useRouter();
const store = useGameStore();

const swapSelected = ref<string[]>([]);

const snapshot = computed(() => store.snapshot);
const me = computed(() =>
  snapshot.value?.players.find((p) => p.seat === snapshot.value?.me)
);

const canDiscard = computed(() => snapshot.value?.available.actions.includes("discard") ?? false);
const canSwap = computed(() => snapshot.value?.phase === "SWAP_TILES");
const canChooseLack = computed(() => snapshot.value?.phase === "CHOOSE_LACK");

const toggleSwapTile = (tile: string) => {
  if (!canSwap.value) {
    if (canDiscard.value) {
      store.sendAction({ action: "discard", tile });
    }
    return;
  }
  const idx = swapSelected.value.indexOf(tile);
  if (idx >= 0) {
    swapSelected.value.splice(idx, 1);
    return;
  }
  if (swapSelected.value.length < 3) {
    swapSelected.value.push(tile);
  }
};

const submitSwap = () => {
  if (swapSelected.value.length !== 3) return;
  store.sendAction({ action: "swap_tiles", tiles: swapSelected.value });
};

const chooseLack = (suit: string) => {
  store.sendAction({ action: "choose_lack", suit });
};

const onAction = (action: string, payload?: Record<string, unknown>) => {
  if (action === "win_self_draw") {
    store.sendAction({ action: "win", type: "self_draw" });
    return;
  }
  if (action === "win") {
    store.sendAction({ action: "win", type: "discard" });
    return;
  }
  if (action === "pong") {
    store.sendAction({ action: "pong" });
    return;
  }
  if (action === "kong_exposed") {
    store.sendAction({ action: "kong", type: "exposed" });
    return;
  }
  if (action === "kong_concealed") {
    store.sendAction({ action: "kong", type: "concealed", tile: payload?.tile });
    return;
  }
  if (action === "pass") {
    store.sendAction({ action: "pass" });
  }
};

onMounted(() => {
  const roomId = String(route.params.id || "");
  const name = String(route.query.name || "Player");
  if (!roomId) {
    router.push("/");
    return;
  }
  store.joinRoom(roomId, name);
});
</script>

<template>
  <main class="game-page">
    <header class="top">
      <h2>房间 {{ store.roomId }}</h2>
      <button class="ready-btn" @click="store.setReady(true)">准备</button>
      <button class="back-btn" @click="router.push('/')">退出</button>
    </header>

    <p v-if="store.error" class="error">{{ store.error }}</p>

    <ScoreBoard
      v-if="snapshot"
      :players="snapshot.players"
      :current-turn="snapshot.current_turn"
    />

    <section class="table" v-if="snapshot">
      <div class="pools">
        <div v-for="p in snapshot.players" :key="p.seat" class="pool-item">
          <h4>{{ p.name }} (Seat {{ p.seat }})</h4>
          <DiscardPool :discards="p.discards" />
        </div>
      </div>

      <div class="my-hand" v-if="me">
        <h3>我的手牌</h3>
        <PlayerHand
          :tiles="me.hand || []"
          :clickable="canDiscard || canSwap"
          @select="toggleSwapTile"
        />
        <p v-if="canSwap">换三张已选: {{ swapSelected.join(", ") || "无" }}</p>
        <button v-if="canSwap" @click="submitSwap">确认换三张</button>
      </div>

      <div v-if="canChooseLack" class="lack">
        <span>选择定缺:</span>
        <button @click="chooseLack('m')">万 (m)</button>
        <button @click="chooseLack('b')">筒 (b)</button>
        <button @click="chooseLack('s')">条 (s)</button>
      </div>

      <ActionBar
        v-if="snapshot.available.actions.length"
        :actions="snapshot.available.actions"
        :target-tile="snapshot.available.target_tile"
        :concealed-kong-tiles="snapshot.available.concealed_kong_tiles"
        @action="onAction"
      />

      <GameResult :result="snapshot.result" />
    </section>

    <aside class="logs">
      <h3>事件日志</h3>
      <div class="log-list">
        <p v-for="line in store.logs" :key="line">{{ line }}</p>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.game-page {
  min-height: 100vh;
  padding: 16px;
  background: linear-gradient(160deg, #e8dfc5, #83a773);
  color: #112b18;
}

.top {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.ready-btn,
.back-btn {
  border: 0;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
}

.ready-btn {
  background: #2f6a2a;
  color: #fff;
}

.back-btn {
  background: #d9d3bb;
}

.error {
  background: #ffe0e0;
  border-radius: 6px;
  padding: 8px;
}

.table {
  margin-top: 12px;
  display: grid;
  gap: 12px;
}

.pools {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 10px;
}

.pool-item {
  background: rgba(255, 255, 255, 0.55);
  border-radius: 8px;
  padding: 8px;
}

.my-hand {
  background: rgba(255, 255, 255, 0.65);
  border-radius: 8px;
  padding: 10px;
}

.lack {
  display: flex;
  gap: 8px;
  align-items: center;
}

.lack button {
  padding: 8px;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  background: #285833;
  color: #fff;
}

.logs {
  margin-top: 14px;
  background: rgba(255, 255, 255, 0.65);
  border-radius: 8px;
  padding: 10px;
}

.log-list {
  max-height: 180px;
  overflow: auto;
}

@media (max-width: 768px) {
  .game-page {
    padding: 10px;
  }
}
</style>

