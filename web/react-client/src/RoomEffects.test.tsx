import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { NightInsects, RoomEffects } from "./RoomEffects";
import type { RoomEffectsSync } from "./types";


const night: RoomEffectsSync = {
  revision: 1,
  room: 42,
  period: "night",
  effects: [
    { id: "wayhouse.frontier_night", visual: { preset: "frontier_wayhouse", intensity: 0.8 } },
    { id: "wayhouse.electric_lamps", visual: { preset: "electric_flicker", period_ms: 6000 } },
    { id: "wayhouse.night_insects", visual: { preset: "night_insects" } },
  ],
};

describe("RoomEffects", () => {
  it("renders the trusted visual presets supplied by the server", () => {
    const markup = renderToStaticMarkup(<><RoomEffects sync={night} /><NightInsects sync={night} /></>);

    expect(markup).toContain("room-effects-frontier-wayhouse");
    expect(markup).toContain("room-effect-flicker");
    expect(markup.match(/room-grasshopper room-grasshopper-/g)).toHaveLength(3);
    expect(markup.match(/room-firefly room-firefly-/g)).toHaveLength(5);
    expect(markup).toContain("firefly-lantern");
    expect(markup).toContain("--grasshopper-duration");
    expect(markup).toContain("--firefly-glow-duration");
  });

  it("renders a quiet default when no character scene is active", () => {
    const markup = renderToStaticMarkup(<><RoomEffects sync={null} /><NightInsects sync={null} /></>);

    expect(markup).not.toContain("room-effect-flicker");
    expect(markup).not.toContain("room-effect-night-insects");
  });
});
