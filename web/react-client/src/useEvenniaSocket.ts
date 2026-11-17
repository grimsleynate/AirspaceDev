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
  onText: (text: string) => void;
  onPrompt: (text: string) => void;
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

function routeStructured(packageName: string, data: unknown, handlers: SocketHandlers): void {
  const normalized = packageName.toLowerCase().replaceAll("_", ".");
  if (normalized === "room.info") handlers.onRoomInfo(data as RoomInfo);
  else if (normalized === "quasar.map.sync") handlers.onMapSync(data as MapSync);
  else if (normalized === "quasar.journal.sync") handlers.onJournalSync(data as JournalSync);
  else if (normalized === "quasar.audio.scene") handlers.onAudioScene(data as AudioScene);
  else if (normalized === "quasar.audio.play") handlers.onAudioPlay(data as AudioPlayEvent);
  else if (normalized === "quasar.audio.stop") handlers.onAudioStop(data as AudioStopEvent);
  else if (normalized === "quasar.room.effects.sync") handlers.onRoomEffects(data as RoomEffectsSync);
  else if (normalized === "quasar.accessibility.sync") handlers.onAccessibility(data as AccessibilitySync);
  else if (normalized === "quasar.character.resources") {
    handlers.onCharacterResources(data as CharacterResourceState);
  }
  else if (normalized === "quasar.chargen.preview") {
    handlers.onChargenPreview(data as ChargenPreview);
  }
  else handlers.onProtocol(packageName, data);
}

export function parseEnvelope(raw: string, handlers: SocketHandlers): void {
  let envelope: { proto?: string; id?: string; data?: string } | [string, unknown, object];
  try {
    envelope = JSON.parse(raw) as typeof envelope;
  } catch {
    return;
  }

  // Evennia's websocket protocol emits [command, args, kwargs]. Text is
  // already safely converted to HTML by Evennia's webclient protocol.
  if (Array.isArray(envelope)) {
    const [command, wireArgs, wireKwargs] = envelope;
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
    return;
  }

  if (envelope.proto === "prompt") {
    handlers.onPrompt(envelope.data || "");
    return;
  }
  if (envelope.proto !== "gmcp" || !envelope.id) {
    handlers.onProtocol(envelope.proto || "unknown", envelope.data);
    return;
  }

  let data: unknown = envelope.data || "";
  try {
    data = envelope.data ? JSON.parse(envelope.data) : {};
  } catch {
    // Some GMCP packages intentionally carry a plain string.
  }

  routeStructured(envelope.id, data, handlers);
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
    socket.binaryType = "arraybuffer";
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("connected");
      const sendGmcp = (name: string, data: unknown = "") => {
        socket.send(
          JSON.stringify([
            "gmcp",
            [
              name,
              typeof data === "string" ? data : JSON.stringify(data),
            ],
            {},
          ]),
        );
      };

      sendGmcp("Quasar.Audio.Supports", { version: 1 });
      sendGmcp("Quasar.Room_Effects.Supports", { version: 1 });
      sendGmcp("Quasar.Accessibility.Get");
      sendGmcp("Quasar.Map.Get");
      sendGmcp("Quasar.Character.Get");
      sendGmcp("Quasar.Journal.Get");
      socket.send(JSON.stringify(["csessid", [config.browserSession || pageId], {}]));
    };
    socket.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        handlersRef.current.onText(new TextDecoder().decode(event.data));
      } else if (event.data instanceof Blob) {
        void event.data.arrayBuffer().then((buffer) => {
          handlersRef.current.onText(new TextDecoder().decode(buffer));
        });
      } else {
        parseEnvelope(String(event.data), handlersRef.current);
      }
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
