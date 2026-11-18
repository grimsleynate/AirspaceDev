import { useState } from "react";

import type { MappedRoom } from "./types";
import { WorldMap } from "./WorldMap";

const definitions = [
  ["nw", -1, 1, "se"], ["n", 0, 1, "s"], ["ne", 1, 1, "sw"],
  ["w", -1, 0, "e"], ["center", 0, 0, ""], ["e", 1, 0, "w"],
  ["sw", -1, -1, "ne"], ["s", 0, -1, "n"], ["se", 1, -1, "nw"],
] as const;

const rooms = Object.fromEntries(
  definitions.map(([id, x, y, reverse]) => {
    const exits: Record<string, string> = id === "center"
      ? {
          ...Object.fromEntries(definitions.filter(([other]) => other !== "center").map(([other]) => [other, other])),
          u: "upper", d: "lower", in: "inside", out: "outside",
        }
      : { [reverse]: "center" };
    return [id, {
      id,
      name: id === "center" ? "Orientation Hall" : `${id.toUpperCase()} Test Room`,
      area: "Mapper Preview",
      environment: "interior",
      exits,
      x,
      y,
      z: 0,
      visited: true,
      description: "A diagnostic room used to preview the mapper.",
      players: [],
      npcs: [],
      items: [], objects: [],
    } satisfies MappedRoom];
  }),
);

export function MapperPreview() {
  const [currentId, setCurrentId] = useState("center");
  const current = rooms[currentId];

  return (
    <main className="mapper-preview">
      <header className="mapper-preview-heading">
        <strong>{current.name}</strong>
        <span>Mapper Preview</span>
      </header>
      <section className="mapper-preview-canvas">
        <WorldMap
          rooms={rooms}
          currentId={currentId}
          onMove={(direction) => {
            const destination = current.exits[direction];
            if (destination) setCurrentId(destination);
          }}
        />
      </section>
    </main>
  );
}
