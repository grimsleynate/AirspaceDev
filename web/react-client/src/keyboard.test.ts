import { describe, expect, it } from "vitest";

import { numpadCommand } from "./keyboard";

describe("numpad navigation", () => {
  it("maps all eight directions and center look", () => {
    expect([
      "Numpad7", "Numpad8", "Numpad9",
      "Numpad4", "Numpad5", "Numpad6",
      "Numpad1", "Numpad2", "Numpad3",
    ].map(numpadCommand)).toEqual([
      "northwest", "north", "northeast",
      "west", "look", "east",
      "southwest", "south", "southeast",
    ]);
  });

  it("ignores non-numpad key codes", () => {
    expect(numpadCommand("Digit8")).toBeNull();
    expect(numpadCommand("ArrowUp")).toBeNull();
  });
});
