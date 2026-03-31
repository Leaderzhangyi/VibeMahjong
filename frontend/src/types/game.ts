export interface PlayerView {
  seat: number;
  name: string;
  ready: boolean;
  score: number;
  lack: string | null;
  tile_count: number;
  hand?: string[];
  discards: string[];
  melds: Array<{ type: string; tiles: string[]; from: number }>;
  last_action: string | null;
}

export interface RoomSnapshot {
  room_id: string;
  phase: string;
  dealer_seat: number;
  current_turn: number | null;
  swap_direction: string | null;
  deck_remaining: number;
  last_discard: string | null;
  last_discard_seat: number | null;
  players: PlayerView[];
  me: number;
  available: {
    actions: string[];
    target_tile?: string;
    concealed_kong_tiles?: string[];
  };
  result: {
    winner: number | null;
    win_type: string;
    fan: number;
    patterns: string[];
    payments: Record<number, number>;
  } | null;
}

