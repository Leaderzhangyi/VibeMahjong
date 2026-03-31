<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const roomId = ref("room-001");
const name = ref(`玩家${Math.floor(Math.random() * 1000)}`);

const start = () => {
  if (!roomId.value || !name.value) return;
  router.push({
    path: `/game/${roomId.value}`,
    query: { name: name.value },
  });
};
</script>

<template>
  <main class="home">
    <h1>四川麻将 Web</h1>
    <div class="panel">
      <label>
        房间号
        <input v-model="roomId" />
      </label>
      <label>
        昵称
        <input v-model="name" />
      </label>
      <button @click="start">进入游戏</button>
    </div>
  </main>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 20% 20%, #ece6cf, #789b66);
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f7f5e8;
  border-radius: 10px;
  padding: 20px;
  min-width: 280px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

input {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #b5ae9a;
}

button {
  padding: 10px;
  border: 0;
  border-radius: 8px;
  background: #2f6a2a;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
</style>

