import { describe, expect, it } from "vitest";

import { commandWithTarget, cycleRoomTarget } from "./targeting";

const targets = [
  { id: 11, name: "Station Guide", hostile: false },
  { id: 12, name: "Scavenger", hostile: true },
];

describe("room targeting", () => {
  it("cycles forward, backward, and around the visible NPC list", () => {
    expect(cycleRoomTarget(targets, null)).toBe("11");
    expect(cycleRoomTarget(targets, "11")).toBe("12");
    expect(cycleRoomTarget(targets, "12")).toBe("11");
    expect(cycleRoomTarget(targets, null, true)).toBe("12");
  });

  it("clears selection when no NPCs are present", () => {
    expect(cycleRoomTarget([], "11")).toBeNull();
  });

  it.each(["attack", "kill", "greet", "talk", "nod", "wave", "smile", "bow", "salute"])(
    "adds the selected dbref to a bare %s command",
    (command) => expect(commandWithTarget(command, targets[1])).toBe(`${command} #12`),
  );

  it("preserves explicit targets and unrelated commands", () => {
    expect(commandWithTarget("attack guide", targets[1])).toBe("attack guide");
    expect(commandWithTarget("look", targets[1])).toBe("look");
    expect(commandWithTarget("attack", null)).toBe("attack");
  });
});
