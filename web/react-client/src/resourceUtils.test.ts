import { describe, expect, it } from "vitest";

import { resourcePercent, visibleResourceBars } from "./resourceUtils";
import type { CharacterResourceState } from "./types";

function state(): CharacterResourceState {
  return {
    revision: 7,
    character: { id: 1, name: "Tester", level: 1 },
    health: { current: 75, max: 100 },
    progression: {
      level: 1,
      experience: 0,
      level_experience: 0,
      level_experience_max: 100,
      next_level_at: 100,
      max_level: 50,
    },
    combat: null,
  };
}

describe("character resource presentation", () => {
  it("shows health for an active character", () => {
    expect(visibleResourceBars(state()).map((bar) => bar.kind)).toEqual(["health"]);
  });

  it("shows nothing without an active character", () => {
    expect(visibleResourceBars({ ...state(), character: null })).toEqual([]);
  });

  it("clamps percentages and handles an empty capacity", () => {
    expect(resourcePercent(125, 100)).toBe(100);
    expect(resourcePercent(-5, 100)).toBe(0);
    expect(resourcePercent(5, 0)).toBe(0);
  });

  it("adds an enemy health meter only while a combat target exists", () => {
    const combatState = state();
    combatState.combat = {
      target: { id: 9, name: "test hostile", level: 1, health: 20, health_max: 50 },
      weapon: "test weapon",
      weapon_family: "melee",
      damage: { min: 7, max: 11 },
      armor: 4,
      accuracy: 11,
      evasion: 5,
      crit_chance: 5,
      recovery_remaining: 0,
    };

    expect(visibleResourceBars(combatState).map((bar) => bar.kind)).toEqual([
      "health", "target",
    ]);
  });
});
