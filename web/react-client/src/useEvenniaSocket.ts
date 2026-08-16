import { useCallback, useEffect, useRef, useState } from "react";

import type {
  AudioPlayEvent,
  AudioScene,
  AudioStopEvent,
  CharacterResourceState,
  ChargenPreview,
  ClientConfig,
  ConnectionStatus,
  MapSync,
  JournalSync,
  RoomInfo,
} from "./types";

interface SocketHandlers {
  onText: (text: string) => void;
  onPrompt: (text: string) => void;
  onRoomInfo: (room: RoomInfo) => void;
  onMapSync: (sync: MapSync) => void;
  onJournalSync: (sync: JournalSync) => void;
  onAudioScene: (scene: AudioScene) => void;
  onAudioPlay: (event: AudioPlayEvent) => void;
  onAudioStop: (event: AudioStopEvent) => void;
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

function parseEnvelope(raw: string, handlers: SocketHandlers): void {
  let envelope: { proto?: string; id?: string; data?: string };
  try {
    envelope = JSON.parse(raw) as typeof envelope;
  } catch {
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

  const packageName = envelope.id.toLowerCase();
  if (packageName === "room.info") handlers.onRoomInfo(data as RoomInfo);
  else if (packageName === "quasar.map.sync") handlers.onMapSync(data as MapSync);
  else if (packageName === "quasar.journal.sync") handlers.onJournalSync(data as JournalSync);
  else if (packageName === "quasar.audio.scene") handlers.onAudioScene(data as AudioScene);
  else if (packageName === "quasar.audio.play") handlers.onAudioPlay(data as AudioPlayEvent);
  else if (packageName === "quasar.audio.stop") handlers.onAudioStop(data as AudioStopEvent);
  else if (packageName === "quasar.character.resources") {
    handlers.onCharacterResources(data as CharacterResourceState);
  }
  else if (packageName === "quasar.chargen.preview") {
    handlers.onChargenPreview(data as ChargenPreview);
  }
  else handlers.onProtocol(envelope.id, data);
}

export function useEvenniaSocket(config: ClientConfig, handlers: SocketHandlers) {
  const socketRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef(handlers);
  const reconnectRef = useRef<number | null>(null);
  const intentionalClose = useRef(false);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  handlersRef.current = handlers;

  const connect = useCallback(() => {
    if (!config.websocketEnabled || socketRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const pageId = crypto.randomUUID?.() || Math.random().toString(36).slice(2);
    const socket = new WebSocket(makeSocketUrl(config, pageId), ["json.mudstandards.org"]);
    socket.binaryType = "arraybuffer";
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("connected");
      socket.send(JSON.stringify({
        proto: "gmcp",
        id: "Quasar.Audio.Supports",
        data: JSON.stringify({ version: 1 }),
      }));
      socket.send(JSON.stringify({ proto: "gmcp", id: "Quasar.Map.Get", data: "" }));
      socket.send(JSON.stringify({ proto: "gmcp", id: "Quasar.Character.Get", data: "" }));
      socket.send(JSON.stringify({ proto: "gmcp", id: "Quasar.Journal.Get", data: "" }));
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
    socket.onerror = () => setStatus("error");
    socket.onclose = () => {
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
        socketRef.current.send(new TextEncoder().encode("idle"));
      }
    }, 180_000);

    return () => {
      intentionalClose.current = true;
      if (reconnectRef.current) window.clearTimeout(reconnectRef.current);
      window.clearInterval(keepAlive);
      const socket = socketRef.current;
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ proto: "websocket_close", id: "", data: "" }));
        socket.close(1000, "Client closed");
      }
    };
  }, [connect]);

  const sendCommand = useCallback((command: string) => {
    const socket = socketRef.current;
    if (!command || socket?.readyState !== WebSocket.OPEN) return false;
    socket.send(new TextEncoder().encode(command));
    return true;
  }, []);

  return { status, sendCommand, reconnect: connect };
}
