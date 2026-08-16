import { Howl, Howler } from "howler";

import { AUDIO_CATALOG, type AudioCatalogEntry, type AudioChannel } from "./audioCatalog";
import type { AudioPlayEvent, AudioScene, AudioSettings, AudioStopEvent } from "./types";

const DEFAULT_FADE_MS = 1_800;
const MAX_SIMULTANEOUS_EFFECTS = 10;

interface ActiveLoop {
  event: string;
  gain: number;
  howl: Howl;
  soundId: number;
}

const clamp = (value: number, minimum = 0, maximum = 1) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? Math.max(minimum, Math.min(maximum, numeric)) : minimum;
};

export const DEFAULT_AUDIO_SETTINGS: AudioSettings = {
  master: 0.8,
  music: 0.42,
  ambience: 0.5,
  effects: 0.72,
};

export class AudioManager {
  private enabled = false;
  private settings: AudioSettings;
  private currentScene: AudioScene | null = null;
  private music: ActiveLoop | null = null;
  private ambience = new Map<string, ActiveLoop>();
  private effectHowls = new Map<string, Howl>();
  private lastPlayed = new Map<string, number>();
  private activeEffects = new Map<string, number>();
  private totalActiveEffects = 0;

  constructor(settings: AudioSettings = DEFAULT_AUDIO_SETTINGS) {
    this.settings = this.sanitizeSettings(settings);
    Howler.volume(this.settings.master);
    Howler.mute(true);
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  async enable(): Promise<void> {
    if (Howler.ctx?.state === "suspended") {
      try {
        await Howler.ctx.resume();
      } catch {
        // Howler will try again on the next browser-approved interaction.
      }
    }
    this.enabled = true;
    Howler.mute(false);
    Howler.volume(this.settings.master);
    if (this.currentScene) this.applyScene(this.currentScene, true);
  }

  disable(): void {
    this.enabled = false;
    Howler.mute(true);
    this.stopActiveLoops(150);
    this.stopEffects();
  }

  destroy(): void {
    this.disable();
    this.effectHowls.forEach((howl) => howl.unload());
    this.effectHowls.clear();
  }

  setSettings(settings: AudioSettings): void {
    this.settings = this.sanitizeSettings(settings);
    Howler.volume(this.settings.master);
    if (this.music) this.setLoopVolume(this.music, "music");
    this.ambience.forEach((loop) => this.setLoopVolume(loop, "ambience"));
  }

  setScene(scene: AudioScene): void {
    this.currentScene = {
      ...scene,
      ambience: Array.isArray(scene.ambience) ? scene.ambience : [],
    };
    if (this.enabled) this.applyScene(this.currentScene, false);
  }

  play(message: AudioPlayEvent): boolean {
    const entry = AUDIO_CATALOG[message.event];
    if (!this.enabled || !entry || entry.channel !== "effects") return false;

    const now = performance.now();
    const cooldown = Math.max(message.cooldown_ms ?? 0, entry.cooldownMs ?? 0);
    if (now - (this.lastPlayed.get(message.event) ?? -Infinity) < cooldown) return false;

    const eventCount = this.activeEffects.get(message.event) ?? 0;
    if (eventCount >= (entry.maxInstances ?? 4) || this.totalActiveEffects >= MAX_SIMULTANEOUS_EFFECTS) {
      return false;
    }

    const variantIndex = Math.floor(Math.random() * entry.variants.length);
    const cacheKey = `${message.event}:${variantIndex}`;
    let howl = this.effectHowls.get(cacheKey);
    if (!howl) {
      howl = new Howl({ src: entry.variants[variantIndex], preload: true });
      this.effectHowls.set(cacheKey, howl);
    }

    const soundId = howl.play();
    howl.volume(this.channelVolume("effects", entry, message.gain), soundId);
    if (typeof message.pan === "number") howl.stereo(clamp(message.pan, -1, 1), soundId);
    this.lastPlayed.set(message.event, now);
    this.activeEffects.set(message.event, eventCount + 1);
    this.totalActiveEffects += 1;

    let released = false;
    const release = () => {
      if (released) return;
      released = true;
      const remaining = Math.max(0, (this.activeEffects.get(message.event) ?? 1) - 1);
      if (remaining) this.activeEffects.set(message.event, remaining);
      else this.activeEffects.delete(message.event);
      this.totalActiveEffects = Math.max(0, this.totalActiveEffects - 1);
    };
    howl.once("end", release, soundId);
    howl.once("playerror", release, soundId);
    return true;
  }

  stop(message: AudioStopEvent): void {
    const fadeMs = clamp(message.fade_ms ?? DEFAULT_FADE_MS, 0, 10_000);
    if (message.all) {
      this.stopActiveLoops(fadeMs);
      this.stopEffects();
      this.currentScene = null;
      return;
    }
    if (message.channel === "music") {
      if (this.music) this.fadeOut(this.music, fadeMs);
      this.music = null;
    } else if (message.channel === "ambience") {
      this.ambience.forEach((loop) => this.fadeOut(loop, fadeMs));
      this.ambience.clear();
    } else if (message.channel === "effects") {
      this.stopEffects();
    } else if (message.event) {
      if (this.music?.event === message.event) {
        this.fadeOut(this.music, fadeMs);
        this.music = null;
      }
      const ambient = this.ambience.get(message.event);
      if (ambient) {
        this.fadeOut(ambient, fadeMs);
        this.ambience.delete(message.event);
      }
      for (const [key, howl] of this.effectHowls) {
        if (key.startsWith(`${message.event}:`)) howl.stop();
      }
    }
  }

  private applyScene(scene: AudioScene, immediate: boolean): void {
    const fadeMs = immediate ? 0 : clamp(scene.fade_ms ?? DEFAULT_FADE_MS, 0, 10_000);
    const musicEvent = scene.music || null;
    if (this.music?.event !== musicEvent) {
      if (this.music) this.fadeOut(this.music, fadeMs);
      this.music = musicEvent ? this.startLoop(musicEvent, 1, fadeMs) : null;
    } else if (this.music) {
      this.setLoopVolume(this.music, "music");
    }

    const desired = new Map((scene.ambience || []).map((layer) => [layer.event, clamp(layer.gain ?? 1)]));
    this.ambience.forEach((loop, event) => {
      if (!desired.has(event)) {
        this.fadeOut(loop, fadeMs);
        this.ambience.delete(event);
      }
    });
    desired.forEach((gain, event) => {
      const active = this.ambience.get(event);
      if (active) {
        active.gain = gain;
        this.setLoopVolume(active, "ambience");
      } else {
        const loop = this.startLoop(event, gain, fadeMs);
        if (loop) this.ambience.set(event, loop);
      }
    });
  }

  private startLoop(event: string, gain: number, fadeMs: number): ActiveLoop | null {
    const entry = AUDIO_CATALOG[event];
    if (!entry || !entry.loop || entry.channel === "effects") return null;
    const howl = new Howl({
      src: entry.variants[0],
      loop: true,
      html5: entry.html5,
      preload: entry.html5 ? "metadata" : true,
    });
    const soundId = howl.play();
    const loop = { event, gain, howl, soundId };
    const target = this.channelVolume(entry.channel, entry, gain);
    if (fadeMs > 0) {
      howl.volume(0, soundId);
      howl.fade(0, target, fadeMs, soundId);
    } else {
      howl.volume(target, soundId);
    }
    return loop;
  }

  private fadeOut(loop: ActiveLoop, fadeMs: number): void {
    const finish = () => {
      loop.howl.stop(loop.soundId);
      loop.howl.unload();
    };
    if (fadeMs <= 0 || !loop.howl.playing(loop.soundId)) {
      finish();
      return;
    }
    loop.howl.fade(loop.howl.volume(loop.soundId) as number, 0, fadeMs, loop.soundId);
    window.setTimeout(finish, fadeMs + 30);
  }

  private stopActiveLoops(fadeMs: number): void {
    if (this.music) this.fadeOut(this.music, fadeMs);
    this.music = null;
    this.ambience.forEach((loop) => this.fadeOut(loop, fadeMs));
    this.ambience.clear();
  }

  private stopEffects(): void {
    this.effectHowls.forEach((howl) => howl.stop());
    this.activeEffects.clear();
    this.totalActiveEffects = 0;
  }

  private setLoopVolume(loop: ActiveLoop, channel: AudioChannel): void {
    const entry = AUDIO_CATALOG[loop.event];
    if (entry) loop.howl.volume(this.channelVolume(channel, entry, loop.gain), loop.soundId);
  }

  private channelVolume(channel: AudioChannel, entry: AudioCatalogEntry, gain = 1): number {
    return clamp(this.settings[channel] * entry.volume * clamp(gain));
  }

  private sanitizeSettings(settings: AudioSettings): AudioSettings {
    return {
      master: clamp(Number(settings.master)),
      music: clamp(Number(settings.music)),
      ambience: clamp(Number(settings.ambience)),
      effects: clamp(Number(settings.effects)),
    };
  }
}
