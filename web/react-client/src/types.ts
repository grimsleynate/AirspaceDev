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
  area_key?: string;
  zone?: string;
  environment?: string;
  terrain?: string;
  exits?: Record<string, string | number>;
  coords?: string;
  coord?: RoomCoordinate;
  description?: string;
  players?: RoomEntity[];
  npcs?: RoomEntity[];
  items?: RoomEntity[];
  objects?: RoomEntity[];
}

export interface EntityAction { label: string; command: string }

export interface RoomEntity {
  id: string | number;
  name: string;
  hostile?: boolean;
  /** Bespoke verbs the server says this entity offers. */
  actions?: EntityAction[];
}

export interface InventoryEntity {
  id: string | number;
  name: string;
  description: string;
  equipable: boolean;
  equipped: boolean;
  container: boolean;
  capacity: number;
  contents_count: number;
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
  description: string;
  players: RoomEntity[];
  npcs: RoomEntity[];
  items: RoomEntity[];
  objects: RoomEntity[];
}

export interface AudioSceneLayer {
  event: string;
  gain?: number;
}

export interface AudioScene {
  revision?: number;
  scene: string;
  music?: string | null;
  ambience?: AudioSceneLayer[];
  fade_ms?: number;
}

export interface AudioPlayEvent {
  revision?: number;
  event: string;
  gain?: number;
  priority?: number;
  cooldown_ms?: number;
  pan?: number;
}

export interface AudioStopEvent {
  revision?: number;
  event?: string;
  channel?: "music" | "ambience" | "effects";
  all?: boolean;
  fade_ms?: number;
}

export interface RoomVisualEffect {
  preset: "night_backdrop" | "electric_flicker" | "night_insects";
  intensity?: number;
  period_ms?: number;
}

export interface RoomEffect {
  id: string;
  visual: RoomVisualEffect;
}

export interface RoomEffectsSync {
  revision: number;
  room: string | number | null;
  period: "day" | "night";
  effects: RoomEffect[];
}

export interface AccessibilitySync {
  revision: number;
  screenreader: boolean;
  color_mode: "auto" | "ansi" | "256" | "truecolor" | "off";
  room_effects: boolean;
  ascii_maps: boolean;
}

export interface AudioSettings {
  master: number;
  music: number;
  ambience: number;
  effects: number;
}

export interface ResourceValue {
  current: number;
  max: number;
}

export interface CharacterResourceState {
  revision: number;
  character: {
    id: string | number;
    name: string;
    level?: number;
  } | null;
  health: ResourceValue | null;
  progression?: {
    level: number;
    experience: number;
    level_experience: number;
    level_experience_max: number;
    next_level_at: number | null;
    max_level: number;
  } | null;
  combat?: {
    target: {
      id: string | number;
      name: string;
      level: number;
      health: number;
      health_max: number;
      intent?: { name: string; resolves_at: number; duration: number } | null;
    } | null;
    weapon: string;
    weapon_family: string;
    attack_category?: "unarmed" | "weapon";
    damage: { min: number; max: number };
    armor: number;
    accuracy: number;
    evasion: number;
    crit_chance: number;
    recovery_remaining: number;
  } | null;
  inventory?: InventoryEntity[];
  equipment?: InventoryEntity[];
}

export interface OutputEntry {
  id: number;
  html: string;
  kind: "text" | "prompt" | "command" | "system";
}
