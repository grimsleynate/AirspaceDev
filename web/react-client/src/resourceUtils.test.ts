import { describe, expect, it } from "vitest";

import { resourcePercent, visibleResourceBars } from "./resourceUtils";
import type { CharacterResourceState } from "./types";

function state(species: "human" | "synth"): CharacterResourceState {
  return {
    revision: 2,
    character: {
      id: 1,
      name: "Test Pilot",
      species,
      career: "Technician",
      specialization: "Engineer",
      level: 1,
    },
    health: { current: 75, max: 100 },
    primary: { kind: "tech", label: "Tech Points", short_label: "Tech", current: 60, max: 100 },
    oxygen: species === "synth"
      ? null
      : { current: 7100, max: 7200, source: "starter oxygen tank", active: true, required: true },
    environment: { atmosphere: "vacuum", breathable: false, gravity: true },
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
  it("shows health, the career resource, and oxygen for organics", () => {
    expect(visibleResourceBars(state("human")).map((bar) => bar.kind)).toEqual([
      "health", "tech", "oxygen",
    ]);
  });

  it("never creates an oxygen meter for a Synth", () => {
    expect(visibleResourceBars(state("synth")).map((bar) => bar.kind)).toEqual([
      "health", "tech",
    ]);
  });

  it("clamps percentages and handles an empty capacity", () => {
    expect(resourcePercent(125, 100)).toBe(100);
    expect(resourcePercent(-5, 100)).toBe(0);
    expect(resourcePercent(5, 0)).toBe(0);
  });

  it("adds an enemy health meter only while a combat target exists", () => {
    const combatState = state("synth");
    combatState.combat = {
      target: { id: 9, name: "training drone", level: 1, health: 20, health_max: 50 },
      weapon: "sidearm",
      weapon_family: "ranged",
      damage: { min: 7, max: 11 },
      armor: 4,
      accuracy: 11,
      evasion: 5,
      crit_chance: 5,
      recovery_remaining: 0,
    };

    expect(visibleResourceBars(combatState).map((bar) => bar.kind)).toEqual([
      "health", "tech", "target",
    ]);
  });
});
