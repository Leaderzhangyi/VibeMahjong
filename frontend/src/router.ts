import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import GameView from "./views/GameView.vue";
import ResultView from "./views/ResultView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomeView },
    { path: "/game/:id", component: GameView, props: true },
    { path: "/result", component: ResultView },
  ],
});

export default router;

