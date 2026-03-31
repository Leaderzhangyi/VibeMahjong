const SUIT_LABELS: Record<string, string> = {
  m: "万",
  s: "条",
  b: "筒",
};

export function tileToLabel(tile: string): string {
  const rank = tile.slice(0, -1);
  const suit = tile.slice(-1);
  if (!rank || !SUIT_LABELS[suit]) {
    return tile;
  }
  return `${rank}${SUIT_LABELS[suit]}`;
}

export function suitToLabel(suit: string | null | undefined): string {
  if (!suit) return "-";
  return SUIT_LABELS[suit] || suit;
}

export function tileIsSuit(tile: string, suit: string | null | undefined): boolean {
  if (!suit) return false;
  return tile.endsWith(suit);
}

