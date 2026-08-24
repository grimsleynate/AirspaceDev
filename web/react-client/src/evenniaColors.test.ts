import { describe, expect, it } from "vitest";

import { EVENNIA_COLOR_CSS, evenniaColorHex } from "./evenniaColors";

describe("Evennia HTML colors", () => {
  it("maps standard and bright ANSI indices to readable theme colors", () => {
    expect(evenniaColorHex(1)).toBe("#c9565d");
    expect(evenniaColorHex(9)).toBe("#ff6e73");
    expect(evenniaColorHex(14)).toBe("#67e8f9");
  });

  it("maps the xterm color cube and grayscale ramp", () => {
    expect(evenniaColorHex(196)).toBe("#ff0000");
    expect(evenniaColorHex(232)).toBe("#080808");
    expect(evenniaColorHex(255)).toBe("#eeeeee");
  });

  it("generates foreground, background, and text-style selectors", () => {
    expect(EVENNIA_COLOR_CSS).toContain(".color-009{color:#ff6e73}");
    expect(EVENNIA_COLOR_CSS).toContain(".bgcolor-196{background-color:#ff0000}");
    expect(EVENNIA_COLOR_CSS).toContain(".underline{text-decoration:underline}");
  });
});
