import { describe, expect, it } from "vitest";
import { hydrateMap, updateMap } from "./mapStore";

describe("updateMap", () => {
  it("stores coordinates and discovers exit targets", () => {
    const result = updateMap({}, null, {
      num: 10, name: "Orientation Hall", area: "Tutorial", coord: { x: 0, y: 0, z: 0 },
      exits: { n: 11, ne: 12, in: 13 },
    });
    expect(result.currentId).toBe("10");
    expect(result.rooms["10"].visited).toBe(true);
    expect(result.rooms["11"]).toMatchObject({ x: 0, y: 1, visited: false });
    expect(result.rooms["12"]).toMatchObject({ x: 1, y: 1, visited: false });
    expect(result.rooms["13"]).toMatchObject({ x: 0, y: 0, visited: false });
  });

  it("infers the next room position from the prior exit", () => {
    const first = updateMap({}, null, { num: 1, name: "A", exits: { sw: 2 } });
    const second = updateMap(first.rooms, "1", { num: 2, name: "B" });
    expect(second.rooms["2"]).toMatchObject({ x: -1, y: -1, z: 0, visited: true });
  });

  it("replaces a placeholder's exits when that room is visited", () => {
    const arrival = updateMap({}, null, {
      num: 1, name: "Arrival", area: "Station", coord: { x: 0, y: 0, z: 0 }, exits: { e: 2 },
    });
    const lock = updateMap(arrival.rooms, "1", {
      num: 2, name: "Lock", area: "Station", coord: { x: 1, y: 0, z: 0 }, exits: { w: 1, e: 3 },
    });

    expect(lock.rooms["2"].exits).toEqual({ w: "1", e: "3" });
    expect(lock.rooms["3"]).toMatchObject({ x: 2, y: 0, area: "Station", visited: false });
  });

  it("repairs stale inferred coordinates for an unvisited adjacent room", () => {
    const stale = {
      "2": {
        id: "2", name: "Unexplored", area: "Old Area", environment: "", exits: {},
        x: 99, y: 99, z: 0, visited: false,
      },
    };
    const result = updateMap(stale, null, {
      num: 1, name: "Hall", area: "Station", coord: { x: 0, y: 0, z: 0 }, exits: { sw: 2 },
    });

    expect(result.rooms["2"]).toMatchObject({ x: -1, y: -1, area: "Station", visited: false });
  });

  it("hydrates an authoritative character snapshot without browser storage", () => {
    const rooms = hydrateMap({
      revision: 1,
      character: { id: 77, name: "Vike" },
      current: 2,
      area: "Station",
      rooms: [
        { num: 1, name: "Dock", area: "Station", coord: { x: 0, y: 0, z: 0 }, exits: { e: 2 } },
        { num: 2, name: "Lock", area: "Station", coord: { x: 1, y: 0, z: 0 }, exits: { w: 1 } },
      ],
    });

    expect(rooms["1"]).toMatchObject({ name: "Dock", visited: true });
    expect(rooms["2"]).toMatchObject({ name: "Lock", visited: true });
    expect(localStorage.length).toBe(0);
  });
});
