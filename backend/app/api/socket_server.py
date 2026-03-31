from __future__ import annotations

import asyncio
import os
from collections import defaultdict

import socketio
from fastapi import FastAPI

from app.game.game_room import GamePhase, GameService


ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else "*",
    logger=False,
    engineio_logger=False,
)
api = FastAPI(title="Sichuan Mahjong Backend", version="0.1.0")
app = socketio.ASGIApp(sio, other_asgi_app=api, socketio_path="ws/socket.io")

service = GameService()
room_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
sid_to_room: dict[str, str] = {}


@api.get("/health")
async def health() -> dict:
    return {"ok": True}


@api.get("/rooms")
async def rooms() -> dict:
    data = {}
    for room_id, room in service.rooms.items():
        data[room_id] = {
            "phase": room.phase.value,
            "players": len(room.sid_to_seat),
            "deck_remaining": room.deck.remaining if room.deck else None,
        }
    return {"rooms": data}


async def emit_room_snapshots(room_id: str) -> None:
    room = service.get_or_create_room(room_id)
    for sid in list(room.sid_to_seat.keys()):
        if sid.startswith("bot:"):
            continue
        try:
            snapshot = room.snapshot_for_sid(sid)
            await sio.emit("snapshot", snapshot, to=sid)
            if room.phase == GamePhase.GAME_OVER and room.result is not None:
                await sio.emit("game_over", room.result.__dict__, to=sid)
        except Exception as exc:  # noqa: BLE001
            await sio.emit("error", {"message": str(exc)}, to=sid)


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None) -> None:  # noqa: ARG001
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid: str) -> None:
    room_id = sid_to_room.pop(sid, None)
    if room_id is None:
        return
    lock = room_locks[room_id]
    async with lock:
        room = service.get_or_create_room(room_id)
        room.leave(sid)
        await sio.leave_room(sid, room_id)
        await emit_room_snapshots(room_id)
        service.maybe_cleanup_room(room_id)


@sio.event
async def join(sid: str, data: dict) -> None:
    room_id = data.get("room_id")
    name = data.get("name", "Player")
    if not room_id:
        await sio.emit("error", {"message": "room_id is required"}, to=sid)
        return

    sid_to_room[sid] = room_id
    await sio.enter_room(sid, room_id)

    lock = room_locks[room_id]
    async with lock:
        room = service.get_or_create_room(room_id)
        try:
            seat = room.join(sid=sid, name=name)
            await sio.emit("joined", {"room_id": room_id, "seat": seat}, to=sid)
            await emit_room_snapshots(room_id)
        except Exception as exc:  # noqa: BLE001
            await sio.emit("error", {"message": str(exc)}, to=sid)


@sio.event
async def ready(sid: str, data: dict | None = None) -> None:
    room_id = sid_to_room.get(sid)
    if room_id is None:
        await sio.emit("error", {"message": "not in room"}, to=sid)
        return
    ready_value = True if data is None else bool(data.get("ready", True))
    lock = room_locks[room_id]
    async with lock:
        room = service.get_or_create_room(room_id)
        try:
            room.set_ready(sid=sid, ready=ready_value)
            room.auto_progress()
            await emit_room_snapshots(room_id)
        except Exception as exc:  # noqa: BLE001
            await sio.emit("error", {"message": str(exc)}, to=sid)


@sio.event
async def action(sid: str, data: dict) -> None:
    room_id = sid_to_room.get(sid)
    if room_id is None:
        await sio.emit("error", {"message": "not in room"}, to=sid)
        return
    action_name = data.get("action")
    lock = room_locks[room_id]
    async with lock:
        room = service.get_or_create_room(room_id)
        try:
            if action_name == "swap_tiles":
                room.choose_swap_tiles(sid=sid, tile_codes=data.get("tiles", []))
            elif action_name == "choose_lack":
                room.choose_lack(sid=sid, suit_value=data.get("suit"))
            elif action_name == "discard":
                room.discard(sid=sid, tile_code=data.get("tile"))
            elif action_name == "pong":
                room.pong(sid=sid)
            elif action_name == "kong":
                kong_type = data.get("type")
                if kong_type == "concealed":
                    room.kong_concealed(sid=sid, tile_code=data.get("tile"))
                elif kong_type == "exposed":
                    room.kong_exposed(sid=sid)
                else:
                    raise ValueError("invalid kong type")
            elif action_name == "win":
                win_type = data.get("type", "discard")
                room.win(sid=sid, win_type=win_type)
            elif action_name == "pass":
                room.pass_action(sid=sid)
            else:
                raise ValueError("unknown action")

            room.auto_progress()
            await sio.emit("event", data, room=room_id)
            await emit_room_snapshots(room_id)
        except Exception as exc:  # noqa: BLE001
            await sio.emit("error", {"message": str(exc)}, to=sid)
