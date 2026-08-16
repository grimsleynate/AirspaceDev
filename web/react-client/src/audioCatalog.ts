export type AudioChannel = "music" | "ambience" | "effects";

export interface AudioCatalogEntry {
  channel: AudioChannel;
  variants: string[][];
  loop?: boolean;
  volume: number;
  html5?: boolean;
  cooldownMs?: number;
  maxInstances?: number;
}

const ROOT = "/static/webclient/audio";
const source = (path: string) => [`${ROOT}/${path}`];

/**
 * Client-owned mapping from semantic game events to trusted, same-origin
 * media. Server messages can select an event but can never make the browser
 * fetch an arbitrary URL.
 */
export const AUDIO_CATALOG: Record<string, AudioCatalogEntry> = {
  "music.quasar_drift": {
    channel: "music",
    variants: [source("music/quasar-drift.mp3")],
    loop: true,
    volume: 0.72,
    html5: true,
  },
  "ambience.station_air": {
    channel: "ambience",
    variants: [source("ambience/station-air.mp3")],
    loop: true,
    volume: 0.6,
    html5: true,
  },
  "ambience.engineering_pulse": {
    channel: "ambience",
    variants: [source("ambience/engineering-pulse.mp3")],
    loop: true,
    volume: 0.48,
    html5: true,
  },
  "ui.confirm": {
    channel: "effects",
    variants: [source("sfx/interface-confirm.mp3")],
    volume: 0.55,
    cooldownMs: 80,
    maxInstances: 2,
  },
  "ui.objective_complete": {
    channel: "effects",
    variants: [source("sfx/objective-complete.mp3")],
    volume: 0.7,
    cooldownMs: 500,
    maxInstances: 1,
  },
  "world.door_open": {
    channel: "effects",
    variants: [source("sfx/door-open-1.ogg"), source("sfx/door-open-2.ogg")],
    volume: 0.7,
    cooldownMs: 120,
    maxInstances: 3,
  },
  "world.door_close": {
    channel: "effects",
    variants: [source("sfx/door-close-1.ogg"), source("sfx/door-close-2.ogg")],
    volume: 0.7,
    cooldownMs: 120,
    maxInstances: 3,
  },
  "world.terminal": {
    channel: "effects",
    variants: [source("sfx/terminal-1.ogg"), source("sfx/terminal-2.ogg")],
    volume: 0.46,
    cooldownMs: 180,
    maxInstances: 2,
  },
  "combat.player_hurt": {
    channel: "effects",
    variants: [
      source("sfx/impact-1.ogg"),
      source("sfx/impact-2.ogg"),
      source("sfx/impact-3.ogg"),
    ],
    volume: 0.78,
    cooldownMs: 150,
    maxInstances: 4,
  },
  "combat.energy_attack": {
    channel: "effects",
    variants: [
      source("sfx/energy-shot-1.ogg"),
      source("sfx/energy-shot-2.ogg"),
      source("sfx/energy-shot-3.ogg"),
    ],
    volume: 0.68,
    cooldownMs: 90,
    maxInstances: 5,
  },
};
