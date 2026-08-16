export const NUMPAD_COMMANDS: Readonly<Record<string, string>> = {
  Numpad7: "northwest",
  Numpad8: "north",
  Numpad9: "northeast",
  Numpad4: "west",
  Numpad5: "look",
  Numpad6: "east",
  Numpad1: "southwest",
  Numpad2: "south",
  Numpad3: "southeast",
};

export function numpadCommand(code: string): string | null {
  return NUMPAD_COMMANDS[code] || null;
}
