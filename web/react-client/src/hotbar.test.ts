import { describe, expect, it } from "vitest";

import {
  buildHotbar, createHotbarProfile, functionKeyIndex, normalizeLearnableCommand,
  recordHotbarCommand,
} from "./hotbar";

describe("adaptive command hotbar", () => {
  it("starts with common actions and the character's active PvE skill", () => {
    const skill = { name: "Breach Strike", command: "cast breach strike" };
    const actions = buildHotbar(createHotbarProfile(skill), skill);

    expect(actions).toHaveLength(10);
    expect(actions.slice(0, 4).map((action) => action.command)).toEqual([
      "attack", "look", "consider", "cast breach strike",
    ]);
    expect(actions[3].label).toBe("Breach Strike");
  });

  it("locks the initial layout during the first nineteen learned commands", () => {
    let profile = createHotbarProfile(null);
    for (let count = 0; count < 19; count += 1) {
      profile = recordHotbarCommand(profile, "TOUCH   PORTER", null, 1_000 + count);
    }

    expect(buildHotbar(profile, null).map((action) => action.command)).not.toContain("touch porter");
  });

  it("promotes only one proven command without moving the pinned slots", () => {
    let profile = createHotbarProfile(null);
    for (let count = 0; count < 20; count += 1) {
      profile = recordHotbarCommand(profile, "TOUCH PORTER", null, 1_000 + count);
    }
    const actions = buildHotbar(profile, null);

    expect(actions.slice(0, 3).map((action) => action.command)).toEqual([
      "attack", "look", "consider",
    ]);
    expect(actions.map((action) => action.command)).toContain("touch porter");
  });

  it("enforces hysteresis and a ten-minute change cooldown", () => {
    let profile = createHotbarProfile(null);
    for (let count = 0; count < 20; count += 1) {
      profile = recordHotbarCommand(profile, "touch porter", null, 1_000 + count);
    }
    const afterFirstChange = profile.adaptiveCommands.join("|");
    for (let count = 0; count < 30; count += 1) {
      profile = recordHotbarCommand(profile, "open cabinet", null, 2_000 + count);
    }

    expect(profile.adaptiveCommands.join("|")).toBe(afterFirstChange);
  });

  it("filters movement, private communication, passwords, and builder commands", () => {
    expect(normalizeLearnableCommand("north")).toBeNull();
    expect(normalizeLearnableCommand("tell Pilot a secret")).toBeNull();
    expect(normalizeLearnableCommand("password hunter2")).toBeNull();
    expect(normalizeLearnableCommand("@dig New Room")).toBeNull();
    expect(normalizeLearnableCommand("set panel = open")).toBeNull();
    expect(normalizeLearnableCommand("touch porter")).toBe("touch porter");
  });

  it("maps only F1 through F10 to hotbar slots", () => {
    expect(functionKeyIndex("F1")).toBe(0);
    expect(functionKeyIndex("F10")).toBe(9);
    expect(functionKeyIndex("F11")).toBeNull();
    expect(functionKeyIndex("1")).toBeNull();
  });
});
