import { defineStore } from "pinia";
import { io, type Socket } from "socket.io-client";
import type { RoomSnapshot } from "../types/game";

interface GameState {
  socket: Socket | null;
  connected: boolean;
  roomId: string;
  name: string;
  mySeat: number | null;
  snapshot: RoomSnapshot | null;
  logs: string[];
  error: string | null;
}

const baseURL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export const useGameStore = defineStore("game", {
  state: (): GameState => ({
    socket: null,
    connected: false,
    roomId: "",
    name: "",
    mySeat: null,
    snapshot: null,
    logs: [],
    error: null,
  }),
  actions: {
    connect() {
      if (this.socket) return this.socket;
      const socket = io(baseURL, {
        transports: ["websocket"],
        path: "/ws/socket.io",
      });
      socket.on("connect", () => {
        this.connected = true;
        this.error = null;
        this.log("已连接服务器");
      });
      socket.on("disconnect", () => {
        this.connected = false;
        this.log("连接断开");
      });
      socket.on("connect_error", (err: Error) => {
        this.connected = false;
        this.error = `连接失败: ${err.message}`;
        this.log(this.error);
      });
      socket.on("joined", (payload: { room_id: string; seat: number }) => {
        this.mySeat = payload.seat;
        this.log(`加入房间 ${payload.room_id}, 座位 ${payload.seat}`);
      });
      socket.on("snapshot", (payload: RoomSnapshot) => {
        this.snapshot = payload;
        if (payload.phase === "GAME_OVER") {
          this.log("对局结束");
        }
      });
      socket.on("event", (payload: Record<string, string>) => {
        this.log(`事件: ${JSON.stringify(payload)}`);
      });
      socket.on("error", (payload: { message: string }) => {
        this.error = payload.message;
        this.log(`错误: ${payload.message}`);
      });
      this.socket = socket;
      return socket;
    },
    joinRoom(roomId: string, name: string) {
      const socket = this.connect();
      this.roomId = roomId;
      this.name = name;

      const emitJoin = () => socket?.emit("join", { room_id: roomId, name });
      if (socket?.connected) {
        emitJoin();
      } else {
        socket?.once("connect", emitJoin);
      }
    },
    setReady(ready = true) {
      this.log(ready ? "已点击准备" : "取消准备");
      this.socket?.emit("ready", { ready });
    },
    sendAction(action: Record<string, unknown>) {
      this.socket?.emit("action", action);
    },
    log(line: string) {
      this.logs.unshift(`${new Date().toLocaleTimeString()} ${line}`);
      this.logs = this.logs.slice(0, 60);
    },
    reset() {
      this.snapshot = null;
      this.logs = [];
      this.error = null;
      this.mySeat = null;
      this.roomId = "";
      this.name = "";
      this.socket?.disconnect();
      this.socket = null;
      this.connected = false;
    },
  },
});

