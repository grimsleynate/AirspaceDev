import type { RoomEntity } from "./types";

const TARGET_OPTIONAL_COMMANDS = new Set([
  "attack",
  "kill",
  "greet",
  "talk",
  "nod",
  "wave",
  "smile",
  "bow",
  "salute",
]);

export function cycleRoomTarget(
  targets: RoomEntity[],
  currentId: string | null,
  reverse = false,
): string | null {
  if (!targets.length) return null;
  const ids = targets.map((target) => String(target.id));
  const currentIndex = currentId === null ? -1 : ids.indexOf(currentId);
  if (currentIndex < 0) return reverse ? ids[ids.length - 1] : ids[0];
  const offset = reverse ? -1 : 1;
  return ids[(currentIndex + offset + ids.length) % ids.length];
}

export function commandWithTarget(command: string, target: RoomEntity | null): string {
  const trimmed = command.trim();
  if (!trimmed || !target) return trimmed;
  const [verb, ...arguments_] = trimmed.split(/\s+/);
  if (arguments_.length || !TARGET_OPTIONAL_COMMANDS.has(verb.toLowerCase())) {
    return trimmed;
  }
  return `${trimmed} #${target.id}`;
}
