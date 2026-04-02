# Sichuan Mahjong Web (MVP)

基于你给出的计划实现了可运行的首版项目骨架，已覆盖：

- 后端 FastAPI + Socket.IO 实时对局
- 四川麻将核心引擎（108 张牌、换三张、定缺、碰/杠/胡、基础番型）
- 前端 Vue3 + TypeScript + Pinia 对局页面
- Docker Compose 一键启动
- 后端单元测试（规则与状态流）

## 目录

```text
backend/
  app/
    api/socket_server.py
    game/
      tile.py
      deck.py
      hand.py
      win_checker.py
      action_checker.py
      score_calculator.py
      game_room.py
  tests/
frontend/
docker-compose.yml
```

## 本地运行

### 1) 后端

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2) 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。

## Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/health`

## 当前已实现规则范围

- 牌型：万/筒/条 1-9，各 4 张，共 108 张
- 流程：准备 -> 换三张 -> 定缺 -> 打牌回合 -> 胡牌/流局
- 动作：出牌、碰、明杠、暗杠、胡、过
- 胡牌：标准 4 面子 + 1 将、七对
- 番型（基础）：平胡、清一色、对对胡、七对、龙七对、自摸、门清、杠上开花、杠上炮、抢杠胡（预留）

## 后续建议（按优先级）

1. 完整四川番型与查叫/查花猪/血战到底细则
2. WebSocket 反应优先级与超时裁决更精细化
3. Redis 房间状态共享（多实例）
4. AI 环境与 PPO 训练管线（`backend/ai`）


## Latest Update (2026-04-02)

- Frontend tile rendering now prefers image assets (`m/s/p*.gif`) with text fallback.
- `DiscardPool` now reuses `TileCard` for visual consistency.
- Added suit normalization (`b -> p`) in tile image mapping to match asset naming.
