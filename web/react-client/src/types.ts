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
  description?: string;
  players?: RoomEntity[];
  npcs?: RoomEntity[];
  items?: RoomEntity[];
}

export interface RoomEntity {
  id: string | number;
  name: string;
  hostile?: boolean;
  readable?: boolean;
  writable?: boolean;
  editable?: boolean;
  journal?: boolean;
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
  readable?: boolean;
  writable?: boolean;
  editable?: boolean;
  journal?: boolean;
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
}

export interface JournalEntry {
  id: string;
  number: number;
  title: string;
  summary: string;
  detail: string;
  status: string;
}

export interface JournalSync {
  revision: number;
  character: { id: string | number; name: string } | null;
  quests: JournalEntry[];
  tasks: JournalEntry[];
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
  preset: "frontier_wayhouse" | "electric_flicker" | "night_insects";
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

export type PrimaryResourceKind = "tech" | "acuity" | "skill";

export interface ResourceValue {
  current: number;
  max: number;
}

export interface PrimaryResource extends ResourceValue {
  kind: PrimaryResourceKind;
  label: string;
  short_label: string;
}

export interface OxygenResource extends ResourceValue {
  source: string | null;
  active: boolean;
  required: boolean;
}

export interface CharacterResourceState {
  revision: number;
  character: {
    id: string | number;
    name: string;
    species: string;
    gender?: string | null;
    pre_synth_gender?: string | null;
    portrait_id?: string;
    portrait_url?: string;
    locomotion_chassis?: "wheel" | "bipedal";
    career: string;
    specialization: string;
    level?: number;
  } | null;
  health: ResourceValue | null;
  primary: PrimaryResource | null;
  oxygen: OxygenResource | null;
  environment: {
    atmosphere: string;
    breathable: boolean;
    gravity: boolean;
  } | null;
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
    attack_category?: "unarmed" | "ranged_energy" | "melee_energy";
    damage: { min: number; max: number };
    armor: number;
    accuracy: number;
    evasion: number;
    crit_chance: number;
    recovery_remaining: number;
    active_skill?: {
      key: string;
      name: string;
      command: string;
    } | null;
  } | null;
  inventory?: InventoryEntity[];
  equipment?: InventoryEntity[];
}

export interface PortraitChoice {
  id: string;
  species: string;
  gender: string;
  label: string;
  url: string;
}

export interface ChargenPreview {
  step: string;
  species: string | null;
  gender: string | null;
  pre_synth_gender: string | null;
  portrait: PortraitChoice | null;
  choices: PortraitChoice[];
}

export interface OutputEntry {
  id: number;
  html: string;
  kind: "text" | "prompt" | "command" | "system";
}
