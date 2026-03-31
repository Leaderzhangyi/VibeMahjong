<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import ActionBar from "../components/ActionBar.vue";
import DiscardPool from "../components/DiscardPool.vue";
import GameResult from "../components/GameResult.vue";
import PlayerHand from "../components/PlayerHand.vue";
import { useGameStore } from "../stores/game";
import { suitToLabel, tileIsSuit, tileToLabel } from "../utils/tile";

const route = useRoute();
const router = useRouter();
const store = useGameStore();

const swapSelected = ref<string[]>([]);

const snapshot = computed(() => store.snapshot);
const mySeat = computed(() => snapshot.value?.me ?? null);

const getRelativePlayer = (offset: number) => {
  if (!snapshot.value || mySeat.value === null) return undefined;
  const seat = (mySeat.value + offset) % 4;
  return snapshot.value.players.find((p) => p.seat === seat);
};

const selfPlayer = computed(() => getRelativePlayer(0));
const rightPlayer = computed(() => getRelativePlayer(1));
const topPlayer = computed(() => getRelativePlayer(2));
const leftPlayer = computed(() => getRelativePlayer(3));

const canDiscard = computed(() => snapshot.value?.available.actions.includes("discard") ?? false);
const canSwap = computed(() => snapshot.value?.phase === "SWAP_TILES");
const canChooseLack = computed(() => snapshot.value?.phase === "CHOOSE_LACK");
const waiting = computed(() => snapshot.value?.phase === "WAITING");
const myReady = computed(() => selfPlayer.value?.ready ?? false);
const myLackSuit = computed(() => selfPlayer.value?.lack || null);

const actionButtons = computed(() =>
  (snapshot.value?.available.actions || []).filter((a) => a !== "discard")
);

const discardableTiles = computed(() => {
  if (!canDiscard.value) return [];
  const hand = selfPlayer.value?.hand || [];
  if (!myLackSuit.value) return hand;
  const hasLack = hand.some((t) => tileIsSuit(t, myLackSuit.value));
  if (!hasLack) return hand;
  return hand.filter((t) => tileIsSuit(t, myLackSuit.value));
});

const toggleSwapOrDiscard = (tile: string) => {
  if (!canSwap.value) {
    if (canDiscard.value) {
      if (!discardableTiles.value.includes(tile)) {
        store.log(`当前必须先打缺门牌: ${suitToLabel(myLackSuit.value)}`);
        return;
      }
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
  const name = String(route.query.name || "玩家");
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
      <div class="status" :class="{ online: store.connected }">
        {{ store.connected ? "已连接" : "未连接" }}
      </div>
      <button class="ready-btn" @click="store.setReady(true)">
        {{ myReady ? "已准备" : "准备开局" }}
      </button>
      <button class="back-btn" @click="router.push('/')">退出</button>
    </header>

    <p v-if="store.error" class="error">{{ store.error }}</p>
    <p v-if="waiting" class="hint">
      {{ myReady ? "等待开局中，系统会自动补机器人..." : "点击“准备开局”开始对局" }}
    </p>

    <section v-if="snapshot" class="board">
      <div class="top-player">
        <p>{{ topPlayer?.name || "对家" }}{{ topPlayer?.is_bot ? " (Bot)" : "" }}</p>
        <div class="concealed">
          <span v-for="n in (topPlayer?.tile_count || 0)" :key="`top-${n}`" class="tile-back" />
        </div>
      </div>

      <div class="left-player">
        <p>{{ leftPlayer?.name || "左家" }}{{ leftPlayer?.is_bot ? " (Bot)" : "" }}</p>
        <div class="concealed vertical">
          <span v-for="n in (leftPlayer?.tile_count || 0)" :key="`left-${n}`" class="tile-back" />
        </div>
      </div>

      <div class="center-table">
        <h3>牌桌中央</h3>
        <p>阶段: {{ snapshot.phase }} | 剩余牌: {{ snapshot.deck_remaining }}</p>
        <p>当前出牌: {{ snapshot.last_discard ? tileToLabel(snapshot.last_discard) : "-" }}</p>
        <div class="center-discards">
          <div v-for="p in snapshot.players" :key="`center-${p.seat}`">
            <strong>{{ p.name }}</strong>
            <DiscardPool :discards="p.discards" />
          </div>
        </div>
      </div>

      <div class="right-player">
        <p>{{ rightPlayer?.name || "右家" }}{{ rightPlayer?.is_bot ? " (Bot)" : "" }}</p>
        <div class="concealed vertical">
          <span v-for="n in (rightPlayer?.tile_count || 0)" :key="`right-${n}`" class="tile-back" />
        </div>
      </div>

      <div class="my-area">
        <p>我的手牌 {{ selfPlayer?.is_bot ? "(Bot)" : "" }}</p>
        <PlayerHand
          :tiles="selfPlayer?.hand || []"
          :clickable="canDiscard || canSwap"
          :allowed-tiles="canDiscard ? discardableTiles : undefined"
          @select="toggleSwapOrDiscard"
        />
        <p v-if="canDiscard && myLackSuit && discardableTiles.length < (selfPlayer?.hand || []).length">
          请先打缺门牌（{{ suitToLabel(myLackSuit) }}）
        </p>
        <p v-if="canSwap">换三张已选: {{ swapSelected.join(", ") || "-" }}</p>
        <button v-if="canSwap" class="primary-btn" @click="submitSwap">确认换三张</button>

        <div v-if="canChooseLack" class="lack">
          <span>选择定缺:</span>
          <button @click="chooseLack('m')">万</button>
          <button @click="chooseLack('b')">筒</button>
          <button @click="chooseLack('s')">条</button>
        </div>

        <ActionBar
          v-if="actionButtons.length"
          :actions="actionButtons"
          :target-tile="snapshot.available.target_tile"
          :concealed-kong-tiles="snapshot.available.concealed_kong_tiles"
          @action="onAction"
        />
      </div>
    </section>

    <GameResult :result="snapshot?.result || null" />

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
  background: radial-gradient(circle at 20% 10%, #f5ecd3, #7ea169);
  color: #1a251d;
}

.top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status {
  padding: 4px 10px;
  border-radius: 999px;
  background: #cc655a;
  color: #fff;
  font-size: 12px;
}

.status.online {
  background: #2f7a42;
}

.ready-btn,
.back-btn,
.primary-btn {
  border: 0;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 700;
}

.ready-btn,
.primary-btn {
  background: #2d6c38;
  color: #fff;
}

.back-btn {
  background: #ded7bf;
}

.hint {
  background: rgba(255, 255, 255, 0.65);
  border-radius: 8px;
  padding: 8px 10px;
  margin-top: 8px;
}

.error {
  background: #ffe5e2;
  border-radius: 8px;
  padding: 8px 10px;
  margin-top: 8px;
}

.board {
  margin-top: 12px;
  display: grid;
  grid-template-areas:
    "top top top"
    "left center right"
    "bottom bottom bottom";
  grid-template-columns: 1fr 2fr 1fr;
  gap: 10px;
}

.top-player,
.left-player,
.right-player,
.center-table,
.my-area {
  background: rgba(255, 255, 255, 0.62);
  border-radius: 10px;
  padding: 10px;
}

.top-player {
  grid-area: top;
}

.left-player {
  grid-area: left;
}

.right-player {
  grid-area: right;
}

.center-table {
  grid-area: center;
}

.my-area {
  grid-area: bottom;
}

.concealed {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.concealed.vertical {
  max-height: 220px;
}

.tile-back {
  width: 22px;
  height: 34px;
  border-radius: 4px;
  background: linear-gradient(145deg, #587f5b, #32563e);
}

.center-discards {
  display: grid;
  gap: 8px;
}

.lack {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.lack button {
  border: 0;
  border-radius: 6px;
  padding: 8px;
  background: #2c5f34;
  color: #fff;
  cursor: pointer;
}

.logs {
  margin-top: 12px;
  background: rgba(255, 255, 255, 0.62);
  border-radius: 8px;
  padding: 10px;
}

.log-list {
  max-height: 200px;
  overflow: auto;
}

@media (max-width: 900px) {
  .board {
    grid-template-areas:
      "top"
      "center"
      "left"
      "right"
      "bottom";
    grid-template-columns: 1fr;
  }
}
</style>
