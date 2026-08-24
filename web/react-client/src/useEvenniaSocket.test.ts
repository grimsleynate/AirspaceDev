import { describe, expect, it, vi } from "vitest";

import { parseEnvelope } from "./useEvenniaSocket";

function handlers() {
  return {
    onText: vi.fn(), onPrompt: vi.fn(), onHtmlText: vi.fn(), onHtmlPrompt: vi.fn(),
    onRoomInfo: vi.fn(), onMapSync: vi.fn(), onJournalSync: vi.fn(),
    onAudioScene: vi.fn(), onAudioPlay: vi.fn(), onAudioStop: vi.fn(), onRoomEffects: vi.fn(), onAccessibility: vi.fn(),
    onCharacterResources: vi.fn(), onChargenPreview: vi.fn(), onProtocol: vi.fn(),
  };
}

describe("Evennia websocket envelopes", () => {
  it("routes native Evennia HTML text packets", () => {
    const target = handlers();

    parseEnvelope(JSON.stringify(["text", ["<span>Welcome to Quasar</span>"], {}]), target);

    expect(target.onHtmlText).toHaveBeenCalledWith("<span>Welcome to Quasar</span>");
  });

  it("routes native structured output names", () => {
    const target = handlers();
    const payload = { revision: 5, character: { id: 7, name: "Pilot" } };

    parseEnvelope(JSON.stringify([
      "quasar_character_resources", [], { ...payload, options: {} },
    ]), target);

    expect(target.onCharacterResources).toHaveBeenCalledWith(payload);
  });

  it("routes native map snapshots carried in Evennia's keyword payload", () => {
    const target = handlers();
    const payload = { revision: 2, current: 9, rooms: [{ id: 9, name: "Airlock" }] };

    parseEnvelope(JSON.stringify(["quasar_map_sync", [], { ...payload, options: {} }]), target);

    expect(target.onMapSync).toHaveBeenCalledWith(payload);
  });

  it("continues to support GMCP JSON envelopes", () => {
    const target = handlers();
    const room = { num: 3, name: "Docking Ring" };

    parseEnvelope(JSON.stringify({
      proto: "gmcp", id: "Room.Info", data: JSON.stringify(room),
    }), target);

    expect(target.onRoomInfo).toHaveBeenCalledWith(room);
  });

  it("routes native room-effect synchronization", () => {
    const target = handlers();
    const payload = { revision: 1, room: 3, period: "night", effects: [] };

    parseEnvelope(JSON.stringify([
      "quasar_room_effects_sync", [], { ...payload, options: {} },
    ]), target);

    expect(target.onRoomEffects).toHaveBeenCalledWith(payload);
  });

  it("routes accessibility preferences", () => {
    const target = handlers();
    const payload = { revision: 1, screenreader: true, color_mode: "off", room_effects: false, ascii_maps: false };

    parseEnvelope(JSON.stringify([
      "quasar_accessibility_sync", [], { ...payload, options: {} },
    ]), target);

    expect(target.onAccessibility).toHaveBeenCalledWith(payload);
  });
});
