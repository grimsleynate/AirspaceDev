/** CSS support for the color-NNN classes emitted by Evennia's TextToHTML parser. */

const ANSI_COLORS = [
  "#5e6b78", "#c9565d", "#65c978", "#d6b956",
  "#668ee8", "#bd7fd3", "#55c4d2", "#d5dfeb",
  "#8795a3", "#ff6e73", "#84e897", "#ffd166",
  "#70a7ff", "#d79aff", "#67e8f9", "#ffffff",
];

export function evenniaColorHex(index: number): string {
  const normalized = Math.max(0, Math.min(255, Math.trunc(index)));
  if (normalized < 16) return ANSI_COLORS[normalized];
  if (normalized < 232) {
    const cube = normalized - 16;
    const red = Math.floor(cube / 36);
    const green = Math.floor((cube % 36) / 6);
    const blue = cube % 6;
    const channel = (value: number) => value === 0 ? 0 : 55 + (value * 40);
    return `#${[red, green, blue]
      .map((value) => channel(value).toString(16).padStart(2, "0"))
      .join("")}`;
  }
  const gray = 8 + ((normalized - 232) * 10);
  const channel = gray.toString(16).padStart(2, "0");
  return `#${channel}${channel}${channel}`;
}

export const EVENNIA_COLOR_CSS = [
  ...Array.from({ length: 256 }, (_, index) => {
    const suffix = String(index).padStart(3, "0");
    const color = evenniaColorHex(index);
    return `.output-entry .color-${suffix}{color:${color}}`;
  }),
  ...Array.from({ length: 256 }, (_, index) => {
    const suffix = String(index).padStart(3, "0");
    const color = evenniaColorHex(index);
    return `.output-entry .bgcolor-${suffix}{background-color:${color}}`;
  }),
  ".output-entry .underline{text-decoration:underline}",
  ".output-entry .blink{animation:evennia-blink 1s steps(1,end) infinite}",
  "@keyframes evennia-blink{50%{opacity:0}}",
].join("");
