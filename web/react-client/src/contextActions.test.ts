import { describe, expect, it } from "vitest";

import { contextActions } from "./contextActions";

const backpack = {
  id: 5, name: "basic backpack", description: "", equipable: false,
  equipped: false, container: true, capacity: 20, contents_count: 0,
};

describe("entity context actions", () => {
  it("offers pickup actions for room items", () => {
    expect(contextActions("room-item", { id: 9, name: "badge" }, backpack)).toEqual([
      { label: "Look", command: "look #9" },
      { label: "Get", command: "get #9" },
    ]);
  });

  it("offers inventory actions based on item capabilities", () => {
    const item = { ...backpack, id: 8, name: "visor", equipable: true, container: false };
    expect(contextActions("inventory", item, backpack).map((action) => action.label)).toEqual([
      "Look", "Drop", "Equip", "Put in basic backpack",
    ]);
  });

  it("offers document actions without exposing author-only edits to others", () => {
    const ownPad = {
      ...backpack, id: 12, name: "flight log", readable: true, writable: true, editable: true,
    };
    expect(contextActions("inventory", ownPad, backpack).map((action) => action.label)).toEqual([
      "Look", "Read", "Write", "Title", "Hack datalog", "Drop", "Put in basic backpack",
    ]);
    expect(contextActions("room-item", { ...ownPad, editable: false }, backpack)
      .map((action) => action.label)).toEqual(["Look", "Read", "Hack datalog", "Get"]);
  });

  it("offers combat for hostiles and conversation for friendly NPCs", () => {
    expect(contextActions("npc", { id: 10, name: "parasite", hostile: true }, undefined)
      .map((action) => action.label)).toContain("Attack");
    const friendly = contextActions("npc", { id: 11, name: "guide" }, undefined)
      .map((action) => action.label);
    expect(friendly).toContain("Greet");
    expect(friendly).toContain("Talk");
  });
});
