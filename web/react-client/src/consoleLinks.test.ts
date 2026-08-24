import { describe, expect, it } from "vitest";

import { commandFromMxpLink } from "./consoleLinks";


describe("Evennia console links", () => {
  it("extracts a literal numbered menu command", () => {
    const host = document.createElement("div");
    host.innerHTML = '<a id="mxplink" href="#" onclick="Evennia.msg(&quot;text&quot;,[&quot;3&quot;],{});return false;">3</a>';
    expect(commandFromMxpLink(host.querySelector("a"))).toBe("3");
  });

  it("keeps displayed text independent from the submitted command", () => {
    const host = document.createElement("div");
    host.innerHTML = '<a id="mxplink" href="#" onclick="Evennia.msg(&quot;text&quot;,[&quot;help ballistics&quot;],{});return false;">Read Ballistics</a>';
    expect(host.textContent).toBe("Read Ballistics");
    expect(commandFromMxpLink(host.querySelector("a"))).toBe("help ballistics");
  });

  it("rejects ordinary and malformed links", () => {
    const ordinary = document.createElement("a");
    ordinary.href = "https://example.com";
    expect(commandFromMxpLink(ordinary)).toBeNull();
    ordinary.id = "mxplink";
    expect(commandFromMxpLink(ordinary)).toBeNull();
  });
});
