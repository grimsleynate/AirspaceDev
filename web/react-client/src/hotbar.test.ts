import { describe, expect, it } from "vitest";

import {
  buildHotbar, createHotbarProfile, functionKeyIndex, normalizeLearnableCommand,
  recordHotbarCommand,
} from "./hotbar";

describe("adaptive command hotbar", () => {
  it("starts with pinned combat actions followed by common commands", () => {
    const actions = buildHotbar(createHotbarProfile());

    expect(actions).toHaveLength(10);
    expect(actions.slice(0, 4).map((action) => action.command)).toEqual([
      "attack", "look", "consider", "sheet",
    ]);
    expect(actions[3].label).toBe("Sheet");
  });

  it("locks the initial layout during the first nineteen learned commands", () => {
    let profile = createHotbarProfile();
    for (let count = 0; count < 19; count += 1) {
      profile = recordHotbarCommand(profile, "OPEN   DOOR", 1_000 + count);
    }

    expect(buildHotbar(profile).map((action) => action.command)).not.toContain("open door");
  });

  it("promotes only one proven command without moving the pinned slots", () => {
    let profile = createHotbarProfile();
    for (let count = 0; count < 20; count += 1) {
      profile = recordHotbarCommand(profile, "OPEN DOOR", 1_000 + count);
    }
    const actions = buildHotbar(profile);

    expect(actions.slice(0, 3).map((action) => action.command)).toEqual([
      "attack", "look", "consider",
    ]);
    expect(actions.map((action) => action.command)).toContain("open door");
  });

  it("enforces hysteresis and a ten-minute change cooldown", () => {
    let profile = createHotbarProfile();
    for (let count = 0; count < 20; count += 1) {
      profile = recordHotbarCommand(profile, "open door", 1_000 + count);
    }
    const afterFirstChange = profile.adaptiveCommands.join("|");
    for (let count = 0; count < 30; count += 1) {
      profile = recordHotbarCommand(profile, "push button", 2_000 + count);
    }

    expect(profile.adaptiveCommands.join("|")).toBe(afterFirstChange);
  });

  it("filters movement, private communication, passwords, and builder commands", () => {
    expect(normalizeLearnableCommand("north")).toBeNull();
    expect(normalizeLearnableCommand("tell Pilot a secret")).toBeNull();
    expect(normalizeLearnableCommand("password hunter2")).toBeNull();
    expect(normalizeLearnableCommand("@dig New Room")).toBeNull();
    expect(normalizeLearnableCommand("set panel = open")).toBeNull();
    expect(normalizeLearnableCommand("open door")).toBe("open door");
  });

  it("maps only F1 through F10 to hotbar slots", () => {
    expect(functionKeyIndex("F1")).toBe(0);
    expect(functionKeyIndex("F10")).toBe(9);
    expect(functionKeyIndex("F11")).toBeNull();
    expect(functionKeyIndex("1")).toBeNull();
  });
});
