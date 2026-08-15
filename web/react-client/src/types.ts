export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

export interface ClientConfig {
  gameName: string;
  browserSession: string;
  websocketEnabled: boolean;
  websocketUrl: string;
  websocketPort: string;
}

export interface RoomCoordinate {
  id?: number;
  x: number;
  y: number;
  z: number;
}

export interface RoomInfo {
  num: string | number;
  name: string;
  area?: string;
  zone?: string;
  environment?: string;
  terrain?: string;
  exits?: Record<string, string | number>;
  coords?: string;
  coord?: RoomCoordinate;
}

export interface MapSync {
  revision: number;
  character: { id: string | number; name: string };
  current: string | number | null;
  area: string | null;
  rooms: RoomInfo[];
}

export interface MappedRoom {
  id: string;
  name: string;
  area: string;
  environment: string;
  exits: Record<string, string>;
  x: number;
  y: number;
  z: number;
  visited: boolean;
}

export interface OutputEntry {
  id: number;
  html: string;
  kind: "text" | "prompt" | "command" | "system";
}
