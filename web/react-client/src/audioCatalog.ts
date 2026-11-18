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
export const AUDIO_CATALOG: Record<string, AudioCatalogEntry> = {};
