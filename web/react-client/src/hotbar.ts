export interface CommandUsage {
  command: string;
  count: number;
  lastUsed: number;
}

export interface HotbarAction {
  command: string;
  label: string;
  score: number;
}

export interface HotbarProfile {
  usage: CommandUsage[];
  adaptiveCommands: string[];
  totalRecorded: number;
  commandsSinceReview: number;
  lastChanged: number;
}

const STORAGE_PREFIX = "quasar.react.hotbar.v2";
const PINNED_COMMANDS = ["attack", "look", "consider"];
const INITIAL_LOCK_COMMANDS = 20;
const REVIEW_INTERVAL_COMMANDS = 12;
const CHANGE_COOLDOWN_MS = 10 * 60 * 1000;
const MIN_CHALLENGER_USES = 5;
const MOVEMENT_COMMANDS = new Set([
  "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest",
  "n", "ne", "e", "se", "s", "sw", "w", "nw", "up", "down", "in", "out",
]);
const PRIVATE_OR_NOISY_COMMANDS = new Set([
  "connect", "create", "password", "passwd", "quit", "logout", "charcreate", "chardelete",
  "say", "tell", "whisper", "page", "pose", "emit", "channels", "channel", "ooc",
  "set", "destroy", "delete", "shutdown", "reload", "reset", "py", "scripts", "objects",
]);

export function normalizeLearnableCommand(raw: string): string | null {
  const command = raw.trim().replace(/\s+/g, " ").toLowerCase();
  if (!command || command.length > 80 || /[\r\n=]/.test(command)) return null;
  const verb = command.split(" ", 1)[0];
  if (
    MOVEMENT_COMMANDS.has(verb) ||
    PRIVATE_OR_NOISY_COMMANDS.has(verb) ||
    verb.startsWith("@") ||
    verb.startsWith("$")
  ) return null;
  return command;
}

export function functionKeyIndex(key: string): number | null {
  const match = /^F([1-9]|10)$/.exec(key);
  return match ? Number(match[1]) - 1 : null;
}

export function recordCommandUsage(
  usage: CommandUsage[],
  raw: string,
  now = Date.now(),
): CommandUsage[] {
  const command = normalizeLearnableCommand(raw);
  if (!command) return usage;
  const existing = usage.find((entry) => entry.command === command);
  const next = existing
    ? usage.map((entry) => entry.command === command
      ? { ...entry, count: Math.min(999, entry.count + 1), lastUsed: now }
      : entry)
    : [...usage, { command, count: 1, lastUsed: now }];
  return next
    .sort((left, right) => right.lastUsed - left.lastUsed)
    .slice(0, 60);
}

function actionLabel(command: string, skillName?: string): string {
  if (skillName && command.startsWith("cast ")) return skillName;
  return command.replace(/\b\w/g, (character) => character.toUpperCase());
}

function initialAdaptiveCommands(activeSkill?: { command: string } | null): string[] {
  return [
    activeSkill?.command || "skills", "inventory", "equipment", "greet", "talk", "map", "vitals",
  ];
}

export function createHotbarProfile(
  activeSkill?: { command: string } | null,
): HotbarProfile {
  return {
    usage: [],
    adaptiveCommands: initialAdaptiveCommands(activeSkill),
    totalRecorded: 0,
    commandsSinceReview: 0,
    lastChanged: 0,
  };
}

function normalizedAdaptiveCommands(
  profile: HotbarProfile,
  activeSkill?: { command: string } | null,
): string[] {
  const preferred = initialAdaptiveCommands(activeSkill);
  const stored = profile.adaptiveCommands.map((command) => (
    command === "skills" && activeSkill?.command ? activeSkill.command : command
  ));
  return [...new Set([...stored, ...preferred])]
    .filter((command) => !PINNED_COMMANDS.includes(command))
    .slice(0, 7);
}

function usageScore(entry: CommandUsage | undefined, now: number): number {
  if (!entry) return 0;
  const ageDays = Math.max(0, now - entry.lastUsed) / 86_400_000;
  return entry.count * (0.5 ** (ageDays / 45));
}

export function recordHotbarCommand(
  profile: HotbarProfile,
  raw: string,
  activeSkill?: { name: string; command: string } | null,
  now = Date.now(),
): HotbarProfile {
  const command = normalizeLearnableCommand(raw);
  if (!command) return profile;
  const usage = recordCommandUsage(profile.usage, command, now);
  const adaptiveCommands = normalizedAdaptiveCommands(profile, activeSkill);
  const next = {
    ...profile,
    usage,
    adaptiveCommands,
    totalRecorded: profile.totalRecorded + 1,
    commandsSinceReview: profile.commandsSinceReview + 1,
  };
  if (
    next.totalRecorded < INITIAL_LOCK_COMMANDS ||
    next.commandsSinceReview < REVIEW_INTERVAL_COMMANDS ||
    (next.lastChanged && now - next.lastChanged < CHANGE_COOLDOWN_MS)
  ) return next;

  const occupied = new Set([...PINNED_COMMANDS, ...adaptiveCommands]);
  const challenger = usage
    .filter((entry) => entry.count >= MIN_CHALLENGER_USES && !occupied.has(entry.command))
    .sort((left, right) => usageScore(right, now) - usageScore(left, now))[0];
  if (!challenger) return { ...next, commandsSinceReview: 0 };

  const weakest = adaptiveCommands
    .map((slotCommand, index) => ({
      command: slotCommand,
      index,
      // A small stability bonus prevents an unused default from disappearing
      // after only a few exploratory commands.
      score: usageScore(usage.find((entry) => entry.command === slotCommand), now) + 2,
    }))
    .sort((left, right) => left.score - right.score || right.index - left.index)[0];
  const challengerScore = usageScore(challenger, now);
  if (challengerScore <= (weakest.score * 1.35) + 2) {
    return { ...next, commandsSinceReview: 0 };
  }
  const commands = [...adaptiveCommands];
  commands[weakest.index] = challenger.command;
  return {
    ...next,
    adaptiveCommands: commands,
    commandsSinceReview: 0,
    lastChanged: now,
  };
}

export function buildHotbar(
  profile: HotbarProfile,
  activeSkill?: { name: string; command: string } | null,
  now = Date.now(),
): HotbarAction[] {
  const commands = [...PINNED_COMMANDS, ...normalizedAdaptiveCommands(profile, activeSkill)];
  return commands.map((command) => ({
    command,
    label: actionLabel(command, activeSkill?.command === command ? activeSkill.name : undefined),
    score: usageScore(profile.usage.find((entry) => entry.command === command), now),
  }));
}

export function loadHotbarProfile(
  characterId: string | number,
  activeSkill?: { command: string } | null,
): HotbarProfile {
  try {
    const value = JSON.parse(localStorage.getItem(`${STORAGE_PREFIX}.${characterId}`) || "null");
    if (!value || Array.isArray(value)) return createHotbarProfile(activeSkill);
    return {
      usage: Array.isArray(value.usage) ? value.usage : [],
      adaptiveCommands: Array.isArray(value.adaptiveCommands)
        ? value.adaptiveCommands
        : initialAdaptiveCommands(activeSkill),
      totalRecorded: Number(value.totalRecorded) || 0,
      commandsSinceReview: Number(value.commandsSinceReview) || 0,
      lastChanged: Number(value.lastChanged) || 0,
    };
  } catch {
    return createHotbarProfile(activeSkill);
  }
}

export function saveHotbarProfile(characterId: string | number, profile: HotbarProfile): void {
  localStorage.setItem(`${STORAGE_PREFIX}.${characterId}`, JSON.stringify(profile));
}
