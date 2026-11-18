import { useCallback, useEffect, useRef, useState } from "react";

import type {
  AudioPlayEvent,
  AccessibilitySync,
  AudioScene,
  AudioStopEvent,
  CharacterResourceState,
  ChargenPreview,
  ClientConfig,
  ConnectionStatus,
  MapSync,
  JournalSync,
  RoomInfo,
  RoomEffectsSync,
} from "./types";

interface SocketHandlers {
  onHtmlText: (html: string) => void;
  onHtmlPrompt: (html: string) => void;
  onRoomInfo: (room: RoomInfo) => void;
  onMapSync: (sync: MapSync) => void;
  onJournalSync: (sync: JournalSync) => void;
  onAudioScene: (scene: AudioScene) => void;
  onAudioPlay: (event: AudioPlayEvent) => void;
  onAudioStop: (event: AudioStopEvent) => void;
  onRoomEffects: (sync: RoomEffectsSync) => void;
  onAccessibility: (sync: AccessibilitySync) => void;
  onCharacterResources: (state: CharacterResourceState) => void;
  onChargenPreview: (preview: ChargenPreview) => void;
  onProtocol: (name: string, data: unknown) => void;
}

function browserName(): string {
  const agent = navigator.userAgent.toLowerCase();
  if (agent.includes("edg")) return "edge";
  if (agent.includes("firefox")) return "firefox";
  if (agent.includes("chrome")) return "chrome";
  if (agent.includes("safari")) return "safari";
  return "browser";
}

function makeSocketUrl(config: ClientConfig, pageId: string): string {
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  const base = config.websocketUrl || `${scheme}://${location.hostname}:${config.websocketPort}`;
  return `${base}?${config.browserSession}&${pageId}&${browserName()}`;
}

// Evennia names websocket output after the Python outputfunc, e.g.
// ``session.msg(quasar_map_sync=...)`` arrives as ``quasar_map_sync``. Telnet
// clients receive the same output as GMCP ``Quasar.Map.Sync`` or MSDP.
function routeStructured(command: string, data: unknown, handlers: SocketHandlers): void {
  switch (command) {
    case "room_info": handlers.onRoomInfo(data as RoomInfo); break;
    case "quasar_map_sync": handlers.onMapSync(data as MapSync); break;
    case "quasar_journal_sync": handlers.onJournalSync(data as JournalSync); break;
    case "quasar_audio_scene": handlers.onAudioScene(data as AudioScene); break;
    case "quasar_audio_play": handlers.onAudioPlay(data as AudioPlayEvent); break;
    case "quasar_audio_stop": handlers.onAudioStop(data as AudioStopEvent); break;
    case "quasar_room_effects_sync": handlers.onRoomEffects(data as RoomEffectsSync); break;
    case "quasar_accessibility_sync": handlers.onAccessibility(data as AccessibilitySync); break;
    case "quasar_character_resources":
      handlers.onCharacterResources(data as CharacterResourceState);
      break;
    case "quasar_chargen_preview": handlers.onChargenPreview(data as ChargenPreview); break;
    default: handlers.onProtocol(command, data);
  }
}

export function parseEnvelope(raw: string, handlers: SocketHandlers): void {
  let envelope: unknown;
  try {
    envelope = JSON.parse(raw);
  } catch {
    return;
  }

  // Evennia's websocket protocol emits [command, args, kwargs]. Text is
  // already safely converted to HTML by Evennia's webclient protocol.
  if (Array.isArray(envelope) && typeof envelope[0] === "string") {
    const [command, wireArgs, wireKwargs] = envelope as [string, unknown, object];
    const args = Array.isArray(wireArgs) ? wireArgs : [wireArgs];
    const kwargs = { ...(wireKwargs || {}) } as Record<string, unknown>;
    delete kwargs.options;
    const data = args.length === 1
      ? args[0]
      : args.length > 1
        ? args
        : kwargs;
    if (command === "text") handlers.onHtmlText(String(data ?? ""));
    else if (command === "prompt") handlers.onHtmlPrompt(String(data ?? ""));
    else routeStructured(command, data, handlers);
  }
}

export function useEvenniaSocket(config: ClientConfig, handlers: SocketHandlers) {
  const socketRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef(handlers);
  const reconnectRef = useRef<number | null>(null);
  const intentionalClose = useRef(false);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  handlersRef.current = handlers;

  const connect = useCallback(() => {
    if (
      !config.websocketEnabled ||
      socketRef.current?.readyState === WebSocket.OPEN ||
      socketRef.current?.readyState === WebSocket.CONNECTING
    ) return;

    setStatus("connecting");
    const pageId = crypto.randomUUID?.() || Math.random().toString(36).slice(2);
    const socket = new WebSocket(makeSocketUrl(config, pageId));
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("connected");
      // Each message names a function in server/conf/inputfuncs.py; telnet
      // clients reach the same functions via GMCP (e.g. Quasar.Map.Get).
      const callInputFunc = (name: string, kwargs: Record<string, unknown> = {}) => {
        socket.send(JSON.stringify([name, [], kwargs]));
      };

      callInputFunc("quasar_audio_supports", { version: 1 });
      callInputFunc("quasar_room_effects_supports", { version: 1 });
      callInputFunc("quasar_accessibility_get");
      callInputFunc("quasar_map_get");
      callInputFunc("quasar_character_get");
      callInputFunc("quasar_journal_get");
      socket.send(JSON.stringify(["csessid", [config.browserSession || pageId], {}]));
    };
    socket.onmessage = (event) => {
      parseEnvelope(String(event.data), handlersRef.current);
    };
    socket.onerror = () => {
      if (socketRef.current === socket) setStatus("error");
    };
    socket.onclose = () => {
      if (socketRef.current !== socket) return;
      socketRef.current = null;
      setStatus("disconnected");
      if (!intentionalClose.current) reconnectRef.current = window.setTimeout(connect, 2500);
    };
  }, [config]);

  useEffect(() => {
    intentionalClose.current = false;
    connect();
    const keepAlive = window.setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify(["text", ["idle"], {}]));
      }
    }, 180_000);

    return () => {
      intentionalClose.current = true;
      if (reconnectRef.current) window.clearTimeout(reconnectRef.current);
      window.clearInterval(keepAlive);
      const socket = socketRef.current;
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(["websocket_close", [], {}]));
      }
      if (socket && socket.readyState !== WebSocket.CLOSED) socket.close(1000, "Client closed");
      if (socketRef.current === socket) socketRef.current = null;
    };
  }, [connect]);

  const sendCommand = useCallback((command: string) => {
    const socket = socketRef.current;
    if (!command || socket?.readyState !== WebSocket.OPEN) return false;
    socket.send(JSON.stringify(["text", [command], {}]));
    return true;
  }, []);


  return { status, sendCommand, reconnect: connect };
}
