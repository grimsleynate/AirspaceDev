import { describe, expect, it } from "vitest";

import { contextActions } from "./contextActions";

const backpack = {
  id: 5, name: "basic backpack", description: "", equipable: false,
  equipped: false, container: true, capacity: 20, contents_count: 0,
};

describe("entity context actions", () => {
  it("offers pickup actions for room items", () => {
    expect(contextActions("room-item", { id: 9, name: "widget" }, backpack)).toEqual([
      { label: "Look", command: "look #9" },
      { label: "Get", command: "get #9" },
    ]);
  });

  it("offers inventory actions based on item capabilities", () => {
    const item = { ...backpack, id: 8, name: "hat", equipable: true, container: false };
    expect(contextActions("inventory", item, backpack).map((action) => action.label)).toEqual([
      "Look", "Drop", "Equip", "Put in basic backpack",
    ]);
  });

  it("offers combat for hostiles and conversation for friendly NPCs", () => {
    expect(contextActions("npc", { id: 10, name: "hostile", hostile: true }, undefined)
      .map((action) => action.label)).toContain("Attack");
    const friendly = contextActions("npc", { id: 11, name: "guide" }, undefined)
      .map((action) => action.label);
    expect(friendly).toContain("Greet");
    expect(friendly).toContain("Talk");
  });
});
