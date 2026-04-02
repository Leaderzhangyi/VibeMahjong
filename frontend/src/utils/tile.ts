const SUIT_LABELS: Record<string, string> = {
  m: "万",
  s: "条",
  b: "筒",
  p: "筒",
};

const tileImageModules = import.meta.glob("../img/*.gif", {
  eager: true,
  import: "default",
}) as Record<string, string>;

const TILE_IMAGES: Record<string, string> = {};

for (const [path, url] of Object.entries(tileImageModules)) {
  const matched = path.match(/([^/\\]+)\.gif$/);
  if (!matched) continue;
  TILE_IMAGES[matched[1]] = url;
}

function normalizeSuitForImage(suit: string): string {
  return suit === "b" ? "p" : suit;
}

export function tileToImage(tile: string): string | null {
  if (!/^\d[mspb]$/.test(tile)) return null;
  const rank = tile[0];
  const suit = normalizeSuitForImage(tile[1]);
  return TILE_IMAGES[`${suit}${rank}`] || null;
}

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
