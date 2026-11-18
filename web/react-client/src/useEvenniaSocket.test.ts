import { describe, expect, it, vi } from "vitest";

import { parseEnvelope } from "./useEvenniaSocket";

function handlers() {
  return {
    onHtmlText: vi.fn(), onHtmlPrompt: vi.fn(),
    onRoomInfo: vi.fn(), onMapSync: vi.fn(),
    onAudioScene: vi.fn(), onAudioPlay: vi.fn(), onAudioStop: vi.fn(), onRoomEffects: vi.fn(), onAccessibility: vi.fn(),
    onCharacterResources: vi.fn(), onProtocol: vi.fn(),
  };
}

describe("Evennia websocket envelopes", () => {
  it("routes native Evennia HTML text packets", () => {
    const target = handlers();

    parseEnvelope(JSON.stringify(["text", ["<span>Welcome</span>"], {}]), target);

    expect(target.onHtmlText).toHaveBeenCalledWith("<span>Welcome</span>");
  });

  it("routes native structured output names", () => {
    const target = handlers();
    const payload = { revision: 5, character: { id: 7, name: "Pilot" } };

    parseEnvelope(JSON.stringify([
      "benben_character_resources", [], { ...payload, options: {} },
    ]), target);

    expect(target.onCharacterResources).toHaveBeenCalledWith(payload);
  });

  it("routes native map snapshots carried in Evennia's keyword payload", () => {
    const target = handlers();
    const payload = { revision: 2, current: 9, rooms: [{ id: 9, name: "Hall" }] };

    parseEnvelope(JSON.stringify(["benben_map_sync", [], { ...payload, options: {} }]), target);

    expect(target.onMapSync).toHaveBeenCalledWith(payload);
  });

  it("routes native room info", () => {
    const target = handlers();
    const room = { num: 3, name: "Courtyard" };

    parseEnvelope(JSON.stringify(["room_info", [], { ...room, options: {} }]), target);

    expect(target.onRoomInfo).toHaveBeenCalledWith(room);
  });

  it("passes unrecognized outputfuncs through untouched", () => {
    const target = handlers();

    parseEnvelope(JSON.stringify(["client_options", [], { ansi: true, options: {} }]), target);

    expect(target.onProtocol).toHaveBeenCalledWith("client_options", { ansi: true });
  });

  it("routes native room-effect synchronization", () => {
    const target = handlers();
    const payload = { revision: 1, room: 3, period: "night", effects: [] };

    parseEnvelope(JSON.stringify([
      "benben_room_effects_sync", [], { ...payload, options: {} },
    ]), target);

    expect(target.onRoomEffects).toHaveBeenCalledWith(payload);
  });

  it("routes accessibility preferences", () => {
    const target = handlers();
    const payload = { revision: 1, screenreader: true, color_mode: "off", room_effects: false, ascii_maps: false };

    parseEnvelope(JSON.stringify([
      "benben_accessibility_sync", [], { ...payload, options: {} },
    ]), target);

    expect(target.onAccessibility).toHaveBeenCalledWith(payload);
  });
});
