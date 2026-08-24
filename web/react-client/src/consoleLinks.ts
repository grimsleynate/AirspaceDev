/** Extract the hidden command from Evennia's server-authored MXP link HTML. */
export function commandFromMxpLink(link: Element | null): string | null {
  if (!link || link.tagName.toLowerCase() !== "a" || link.getAttribute("id") !== "mxplink") {
    return null;
  }
  const handler = (link.getAttribute("onclick") || "").replaceAll("&quot;", '"');
  const match = /Evennia\.msg\(\s*"text"\s*,\s*\[\s*("(?:\\.|[^"\\])*")\s*\]/.exec(handler);
  if (!match) return null;
  try {
    const command = JSON.parse(match[1]) as unknown;
    return typeof command === "string" && command.trim() ? command : null;
  } catch {
    return null;
  }
}
