import { describe, expect, it } from "vitest";

import type { MappedRoom } from "./types";
import { buildMapElements } from "./WorldMap";

function room(id: string, x: number, y: number, exits: Record<string, string>): MappedRoom {
  return {
    id,
    name: `Room ${id}`,
    area: "Test Area",
    environment: "interior",
    exits,
    x,
    y,
    z: 0,
    visited: true,
    description: "",
    players: [],
    npcs: [],
    items: [], objects: [],
  };
}

describe("buildMapElements", () => {
  it("connects cardinal rooms through opposing side handles", () => {
    const result = buildMapElements(
      {
        center: room("center", 0, 0, { e: "east" }),
        east: room("east", 1, 0, { w: "center" }),
      },
      "center",
    );

    expect(result.edges).toHaveLength(1);
    expect(result.edges[0]).toMatchObject({
      source: "center",
      target: "east",
      sourceHandle: "e-source",
      targetHandle: "w-target",
      type: "straight",
    });
  });

  it("connects diagonal rooms through opposing corner handles", () => {
    const result = buildMapElements(
      {
        center: room("center", 0, 0, { ne: "northeast" }),
        northeast: room("northeast", 1, 1, { sw: "center" }),
      },
      "center",
    );

    expect(result.edges[0]).toMatchObject({
      sourceHandle: "ne-source",
      targetHandle: "sw-target",
    });
  });

  it("keeps room names as accessibility labels instead of visible node data", () => {
    const result = buildMapElements({ center: room("center", 0, 0, {}) }, "center");

    expect(result.nodes[0].ariaLabel).toBe("Room center. No visible exits");
    expect(result.nodes[0].data).not.toHaveProperty("label");
  });

  it("stores visible compass and special exits for room icon indicators", () => {
    const result = buildMapElements(
      { center: room("center", 0, 0, { n: "north", sw: "southwest", u: "upper", in: "inside" }) },
      "center",
    );

    expect(result.nodes[0].data.exitDirections).toEqual(["n", "sw", "u", "in"]);
    expect(result.nodes[0].ariaLabel).toContain("north, southwest, up, in");
  });
});
