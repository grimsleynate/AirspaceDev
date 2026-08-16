import { describe, expect, it } from "vitest";

import { AUDIO_CATALOG } from "./audioCatalog";

describe("audio catalog", () => {
  it("contains the starter scene and gameplay events", () => {
    expect(AUDIO_CATALOG).toHaveProperty("music.quasar_drift");
    expect(AUDIO_CATALOG).toHaveProperty("ambience.station_air");
    expect(AUDIO_CATALOG).toHaveProperty("combat.player_hurt");
    expect(AUDIO_CATALOG).toHaveProperty("combat.energy_attack");
  });

  it("only resolves semantic ids to trusted same-origin static assets", () => {
    for (const [event, entry] of Object.entries(AUDIO_CATALOG)) {
      expect(event).toMatch(/^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/);
      expect(entry.variants.length).toBeGreaterThan(0);
      for (const variant of entry.variants) {
        expect(variant.length).toBeGreaterThan(0);
        for (const source of variant) {
          expect(source).toMatch(/^\/static\/webclient\/audio\//);
          expect(source).not.toMatch(/^https?:/);
        }
      }
    }
  });

  it("marks music and ambience as loops but effects as one-shots", () => {
    for (const entry of Object.values(AUDIO_CATALOG)) {
      if (entry.channel === "effects") expect(entry.loop).not.toBe(true);
      else expect(entry.loop).toBe(true);
    }
  });
});
