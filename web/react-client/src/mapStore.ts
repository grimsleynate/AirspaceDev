import type { MappedRoom, MapSync, RoomInfo } from "./types";

const vectors: Record<string, [number, number, number]> = {
  n: [0, 1, 0], ne: [1, 1, 0], e: [1, 0, 0], se: [1, -1, 0],
  s: [0, -1, 0], sw: [-1, -1, 0], w: [-1, 0, 0], nw: [-1, 1, 0],
  u: [0, 0, 1], d: [0, 0, -1], in: [0, 0, 0], out: [0, 0, 0],
};

function coordinates(info: RoomInfo): [number, number, number] | null {
  if (info.coord && Number.isFinite(Number(info.coord.x)) && Number.isFinite(Number(info.coord.y))) {
    return [Number(info.coord.x), Number(info.coord.y), Number(info.coord.z || 0)];
  }
  if (info.coords) {
    const values = info.coords.split(",").map(Number);
    if (values.length >= 3 && Number.isFinite(values[1]) && Number.isFinite(values[2])) {
      return [values[1], values[2], Number(values[3] || 0)];
    }
  }
  return null;
}

export function updateMap(
  rooms: Record<string, MappedRoom>,
  currentId: string | null,
  info: RoomInfo,
): { rooms: Record<string, MappedRoom>; currentId: string } {
  const id = String(info.num);
  const prior = currentId ? rooms[currentId] : undefined;
  let position = coordinates(info);

  if (!position && rooms[id]) position = [rooms[id].x, rooms[id].y, rooms[id].z];
  if (!position && prior) {
    const direction = Object.keys(prior.exits).find((key) => prior.exits[key] === id);
    const vector = direction ? vectors[direction.toLowerCase()] : undefined;
    if (vector) position = [prior.x + vector[0], prior.y + vector[1], prior.z + vector[2]];
  }
  position ||= [0, 0, 0];

  const next = { ...rooms };
  const oldRoom = rooms[id];
  const exits = Object.fromEntries(
    Object.entries(info.exits || {}).map(([direction, target]) => [direction.toLowerCase(), String(target)]),
  );
  next[id] = {
    id,
    name: info.name || oldRoom?.name || `Room ${id}`,
    area: info.area || info.zone || oldRoom?.area || "Uncharted",
    environment: info.environment || info.terrain || oldRoom?.environment || "",
    exits,
    x: position[0], y: position[1], z: position[2], visited: true,
    description: info.description ?? oldRoom?.description ?? "",
    players: info.players ?? oldRoom?.players ?? [],
    npcs: info.npcs ?? oldRoom?.npcs ?? [],
    items: info.items ?? oldRoom?.items ?? [],
    objects: info.objects ?? oldRoom?.objects ?? [],
  };

  Object.entries(exits).forEach(([direction, targetId]) => {
    const vector = vectors[direction] || [0, 0, 0];
    const target = next[targetId];
    // A placeholder is inferred from the current room. Recompute it whenever
    // we see the exit so stale inferred positions cannot survive a map update.
    if (!target || !target.visited) {
      next[targetId] = {
        id: targetId,
        name: target?.name || "Unexplored",
        area: next[id].area,
        environment: target?.environment || "",
        exits: target?.exits || {},
        x: position[0] + vector[0],
        y: position[1] + vector[1],
        z: position[2] + vector[2],
        visited: false,
        description: target?.description || "",
        players: target?.players || [],
        npcs: target?.npcs || [],
        items: target?.items || [],
        objects: target?.objects || [],
      };
    }
  });
  return { rooms: next, currentId: id };
}

export function hydrateMap(sync: MapSync): Record<string, MappedRoom> {
  let rooms: Record<string, MappedRoom> = {};
  for (const info of sync.rooms) {
    rooms = updateMap(rooms, null, info).rooms;
  }
  return rooms;
}
