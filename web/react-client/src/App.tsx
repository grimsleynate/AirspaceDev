import { useCallback, useEffect, useMemo, useRef, useState, type MouseEvent as ReactMouseEvent } from "react";
import {
  Box, Button, Chip, CssBaseline, Divider, Drawer, IconButton, Menu, MenuItem, Paper,
  Slider, Stack, Tab, Tabs, TextField, ThemeProvider, Tooltip, Typography, createTheme,
} from "@mui/material";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import MapOutlinedIcon from "@mui/icons-material/MapOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import TravelExploreOutlinedIcon from "@mui/icons-material/TravelExploreOutlined";
import VolumeOffRoundedIcon from "@mui/icons-material/VolumeOffRounded";
import VolumeUpRoundedIcon from "@mui/icons-material/VolumeUpRounded";

import { AudioManager, DEFAULT_AUDIO_SETTINGS } from "./AudioManager";
import { ansiToHtml, looksLikePasswordPrompt } from "./ansi";
import { contextActions, type EntityContext } from "./contextActions";
import { commandFromMxpLink } from "./consoleLinks";
import { EVENNIA_COLOR_CSS } from "./evenniaColors";
import { hydrateMap, updateMap } from "./mapStore";
import {
  buildHotbar, createHotbarProfile, functionKeyIndex, loadHotbarProfile,
  recordHotbarCommand, saveHotbarProfile,
} from "./hotbar";
import { numpadCommand } from "./keyboard";
import { ResourceHud } from "./ResourceHud";
import { NightInsects, RoomEffects } from "./RoomEffects";
import { commandWithTarget, cycleRoomTarget } from "./targeting";
import type {
  AccessibilitySync, AudioSettings, CharacterResourceState, ChargenPreview, ClientConfig, JournalEntry, JournalSync, MapSync,
  InventoryEntity, MappedRoom, OutputEntry, RoomEntity, RoomEffectsSync, RoomInfo,
} from "./types";
import { useEvenniaSocket } from "./useEvenniaSocket";
import { WorldMap } from "./WorldMap";

const MAX_OUTPUT_ENTRIES = 500;
const MAP_VISIBLE_KEY = "quasar.react.mapper.visible.v1";
const FONT_SIZE_KEY = "quasar.react.font-size.v1";
const AUDIO_ENABLED_KEY = "quasar.react.audio.enabled.v1";
const AUDIO_SETTINGS_KEY = "quasar.react.audio.settings.v1";

function loadAudioSettings(): AudioSettings {
  try {
    const saved = JSON.parse(localStorage.getItem(AUDIO_SETTINGS_KEY) || "null") as Partial<AudioSettings> | null;
    return saved ? { ...DEFAULT_AUDIO_SETTINGS, ...saved } : DEFAULT_AUDIO_SETTINGS;
  } catch {
    return DEFAULT_AUDIO_SETTINGS;
  }
}

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#59d9ff" },
    secondary: { main: "#c996ff" },
    background: { default: "#030711", paper: "#08111f" },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    button: { textTransform: "none", fontWeight: 700 },
  },
  shape: { borderRadius: 10 },
});

interface AppProps { config: ClientConfig }

function newEntry(id: number, text: string, kind: OutputEntry["kind"]): OutputEntry {
  return { id, html: ansiToHtml(text), kind };
}

function newHtmlEntry(id: number, html: string, kind: OutputEntry["kind"]): OutputEntry {
  return { id, html, kind };
}

function EntityLine({ label, entities, tone, selectedId = null, onSelect }: {
  label: string;
  entities: RoomEntity[];
  tone: "item" | "player" | "npc";
  selectedId?: string | null;
  onSelect?: (event: ReactMouseEvent, entity: RoomEntity) => void;
}) {
  return (
    <Box className="room-entity-line">
      <Typography component="span" className="room-entity-label">{label}:</Typography>{" "}
      {entities.length ? entities.map((entity, index) => (
        <Typography
          component="span"
          key={`${entity.id}-${index}`}
          className={`room-entity room-entity-${entity.hostile ? "hostile" : tone}${selectedId === String(entity.id) ? " room-entity-targeted" : ""}`}
          onClick={onSelect ? (event) => onSelect(event, entity) : undefined}
          role={onSelect ? "button" : undefined}
          aria-current={selectedId === String(entity.id) ? "true" : undefined}
        >
          {index ? ", " : ""}{entity.name}
        </Typography>
      )) : <Typography component="span" className="room-entity-empty">None.</Typography>}
    </Box>
  );
}

interface ActionMenuState {
  x: number;
  y: number;
  context: EntityContext;
  entity: RoomEntity | InventoryEntity;
}

function JournalList({ entries, kind, run }: {
  entries: JournalEntry[]; kind: "quest" | "task"; run: (command: string) => void;
}) {
  if (!entries.length) {
    return <Typography color="text.secondary">You have no active {kind}s.</Typography>;
  }
  return (
    <Stack spacing={1}>
      {entries.map((entry) => (
        <Button
          key={entry.id}
          className="journal-entry"
          onClick={() => run(`${kind} ${entry.number}`)}
        >
          <Box>
            <Typography className="journal-title">{entry.number}. {entry.title}</Typography>
            <Typography variant="body2" color="text.secondary">{entry.summary}</Typography>
            <Typography variant="caption" className="journal-detail">{entry.detail}</Typography>
          </Box>
        </Button>
      ))}
    </Stack>
  );
}

export default function App({ config }: AppProps) {
  const [entries, setEntries] = useState<OutputEntry[]>([]);
  const [rooms, setRooms] = useState<Record<string, MappedRoom>>({});
  const [currentRoomId, setCurrentRoomId] = useState<string | null>(null);
  const [selectedTargetId, setSelectedTargetId] = useState<string | null>(null);
  const [actionMenu, setActionMenu] = useState<ActionMenuState | null>(null);
  const [characterResources, setCharacterResources] = useState<CharacterResourceState | null>(null);
  const [chargenPreview, setChargenPreview] = useState<ChargenPreview | null>(null);
  const [command, setCommand] = useState("");
  const [hotbarProfile, setHotbarProfile] = useState(() => createHotbarProfile(null));
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [secretInput, setSecretInput] = useState(false);
  const [leftTab, setLeftTab] = useState(0);
  const [rightTab, setRightTab] = useState(0);
  const [journal, setJournal] = useState<JournalSync | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mapVisible, setMapVisible] = useState(
    () => localStorage.getItem(MAP_VISIBLE_KEY) !== "false",
  );
  const [fontSize, setFontSize] = useState(
    () => Number(localStorage.getItem(FONT_SIZE_KEY) || 15),
  );
  const [audioSettings, setAudioSettings] = useState<AudioSettings>(loadAudioSettings);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [roomEffects, setRoomEffects] = useState<RoomEffectsSync | null>(null);
  const [accessibility, setAccessibility] = useState<AccessibilitySync | null>(null);
  const nextId = useRef(1);
  const outputEnd = useRef<HTMLDivElement | null>(null);
  const currentRoomIdRef = useRef<string | null>(null);
  const audioWantedRef = useRef(localStorage.getItem(AUDIO_ENABLED_KEY) === "true");
  const audioManagerRef = useRef<AudioManager | null>(null);
  if (!audioManagerRef.current) audioManagerRef.current = new AudioManager(audioSettings);

  const enableAudio = useCallback(async () => {
    const manager = audioManagerRef.current;
    if (!manager) return;
    await manager.enable();
    setAudioEnabled(true);
    audioWantedRef.current = true;
    localStorage.setItem(AUDIO_ENABLED_KEY, "true");
    manager.play({ event: "ui.confirm" });
  }, []);

  const disableAudio = useCallback(() => {
    audioManagerRef.current?.disable();
    setAudioEnabled(false);
    audioWantedRef.current = false;
    localStorage.setItem(AUDIO_ENABLED_KEY, "false");
  }, []);

  const toggleAudio = () => {
    if (audioEnabled) disableAudio();
    else void enableAudio();
  };

  const updateAudioSetting = (key: keyof AudioSettings, value: number) => {
    setAudioSettings((current) => {
      const next = { ...current, [key]: value };
      localStorage.setItem(AUDIO_SETTINGS_KEY, JSON.stringify(next));
      audioManagerRef.current?.setSettings(next);
      return next;
    });
  };

  const append = (text: string, kind: OutputEntry["kind"] = "text") => {
    if (!text) return;
    setEntries((current) => [
      ...current.slice(-(MAX_OUTPUT_ENTRIES - 1)),
      newEntry(nextId.current++, text, kind),
    ]);
    if (looksLikePasswordPrompt(text)) setSecretInput(true);
  };

  const appendHtml = (html: string, kind: OutputEntry["kind"] = "text") => {
    if (!html) return;
    setEntries((current) => [
      ...current.slice(-(MAX_OUTPUT_ENTRIES - 1)),
      newHtmlEntry(nextId.current++, html, kind),
    ]);
    if (looksLikePasswordPrompt(html.replace(/<[^>]*>/g, ""))) setSecretInput(true);
  };

  const handlers = useMemo(
    () => ({
      onText: (text: string) => append(text, "text"),
      onPrompt: (text: string) => append(text, "prompt"),
      onHtmlText: (html: string) => appendHtml(html, "text"),
      onHtmlPrompt: (html: string) => appendHtml(html, "prompt"),
      onRoomInfo: (info: RoomInfo) => {
        const previousRoomId = currentRoomIdRef.current;
        const nextRoomId = String(info.num);
        currentRoomIdRef.current = nextRoomId;
        setCurrentRoomId(nextRoomId);
        setRooms((current) => {
          return updateMap(current, previousRoomId, info).rooms;
        });
      },
      onMapSync: (sync: MapSync) => {
        const nextRoomId = sync.current === null ? null : String(sync.current);
        currentRoomIdRef.current = nextRoomId;
        setCurrentRoomId(nextRoomId);
        setRooms(hydrateMap(sync));
      },
      onJournalSync: (sync: JournalSync) => setJournal(sync.character ? sync : null),
      onAudioScene: (scene: Parameters<AudioManager["setScene"]>[0]) => {
        audioManagerRef.current?.setScene(scene);
      },
      onAudioPlay: (event: Parameters<AudioManager["play"]>[0]) => {
        audioManagerRef.current?.play(event);
      },
      onAudioStop: (event: Parameters<AudioManager["stop"]>[0]) => {
        audioManagerRef.current?.stop(event);
      },
      onRoomEffects: (sync: RoomEffectsSync) => setRoomEffects(sync),
      onAccessibility: (sync: AccessibilitySync) => {
        setAccessibility(sync);
        if (!sync.room_effects || sync.screenreader) {
          audioManagerRef.current?.disable();
          setAudioEnabled(false);
        }
      },
      onCharacterResources: (resources: CharacterResourceState) => {
        setCharacterResources(resources.character ? resources : null);
        if (resources.character) setChargenPreview(null);
      },
      onChargenPreview: (preview: ChargenPreview) => setChargenPreview(preview),
      onProtocol: (_name: string, _data: unknown) => undefined,
    }),
    [],
  );
  const { status, sendCommand, reconnect } = useEvenniaSocket(config, handlers);
  const currentRoom = currentRoomId ? rooms[currentRoomId] : undefined;
  const roomTargets = currentRoom?.npcs || [];
  const selectedTarget = roomTargets.find(
    (target) => String(target.id) === selectedTargetId,
  ) || null;
  const inventory = characterResources?.inventory || [];
  const equipment = characterResources?.equipment || [];
  const backpack = inventory.find((item) => item.container);
  const characterId = characterResources?.character?.id;
  const hotbarActions = useMemo(
    () => buildHotbar(hotbarProfile, characterResources?.combat?.active_skill),
    [hotbarProfile, characterResources?.combat?.active_skill],
  );

  useEffect(() => {
    setHotbarProfile(
      characterId === undefined
        ? createHotbarProfile(null)
        : loadHotbarProfile(characterId, characterResources?.combat?.active_skill),
    );
  }, [characterId, characterResources?.combat?.active_skill?.command]);

  const rememberCommand = useCallback((value: string) => {
    if (characterId === undefined) return;
    setHotbarProfile((current) => {
      const next = recordHotbarCommand(
        current,
        value,
        characterResources?.combat?.active_skill,
      );
      if (next !== current) saveHotbarProfile(characterId, next);
      return next;
    });
  }, [characterId, characterResources?.combat?.active_skill]);

  const openActionMenu = (
    event: ReactMouseEvent,
    context: EntityContext,
    entity: RoomEntity | InventoryEntity,
  ) => {
    event.preventDefault();
    if (context === "npc") setSelectedTargetId(String(entity.id));
    setActionMenu({ x: event.clientX, y: event.clientY, context, entity });
  };

  useEffect(() => {
    if (selectedTargetId && !roomTargets.some((target) => String(target.id) === selectedTargetId)) {
      setSelectedTargetId(null);
    }
  }, [currentRoomId, roomTargets, selectedTargetId]);

  useEffect(() => {
    const handleTargetCycle = (event: KeyboardEvent) => {
      if (
        event.key !== "Tab" ||
        !characterResources?.character ||
        secretInput ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.repeat
      ) return;
      event.preventDefault();
      event.stopPropagation();
      setSelectedTargetId((current) => cycleRoomTarget(roomTargets, current, event.shiftKey));
    };
    window.addEventListener("keydown", handleTargetCycle, { capture: true });
    return () => window.removeEventListener("keydown", handleTargetCycle, { capture: true });
  }, [characterResources?.character, roomTargets, secretInput]);

  useEffect(() => {
    const handleNumpad = (event: KeyboardEvent) => {
      const movement =
        characterResources?.character &&
        !secretInput &&
        !command &&
        !event.altKey &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.repeat
          ? numpadCommand(event.code)
          : null;
      if (!movement || !sendCommand(movement)) return;
      event.preventDefault();
      event.stopPropagation();
      append(`> ${movement}`, "command");
    };
    window.addEventListener("keydown", handleNumpad, { capture: true });
    return () => window.removeEventListener("keydown", handleNumpad, { capture: true });
  }, [characterResources?.character, command, secretInput, sendCommand]);

  useEffect(() => {
    outputEnd.current?.scrollIntoView({ block: "end" });
  }, [entries]);

  useEffect(() => {
    // The old keys contained one map shared by every character. Since their
    // ownership is unknowable, discard them rather than migrate bad data.
    localStorage.removeItem("quasar.react.mapper.rooms.v1");
    localStorage.removeItem("quasar.react.mapper.rooms.v2");
  }, []);

  useEffect(() => {
    if (!audioWantedRef.current || audioEnabled) return;
    const unlock = () => void enableAudio();
    window.addEventListener("pointerdown", unlock, { once: true });
    window.addEventListener("keydown", unlock, { once: true });
    return () => {
      window.removeEventListener("pointerdown", unlock);
      window.removeEventListener("keydown", unlock);
    };
  }, [audioEnabled, enableAudio]);

  const submit = () => {
    const value = command.trim();
    const outgoing = commandWithTarget(value, selectedTarget);
    if (!value || !sendCommand(outgoing)) return;
    if (!secretInput) {
      append(`> ${value}`, "command");
      rememberCommand(value);
      setHistory((current) => [...current.filter((item) => item !== value), value].slice(-100));
    }
    setHistoryIndex(0);
    setCommand("");
    setSecretInput(false);
  };

  const run = (value: string) => {
    if (!sendCommand(commandWithTarget(value, selectedTarget))) return;
    append(`> ${value}`, "command");
    rememberCommand(value);
  };

  const runConsoleLink = (event: ReactMouseEvent<HTMLElement>) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const link = target.closest('a[id="mxplink"]');
    const value = commandFromMxpLink(link);
    if (!value) return;
    // Capture prevents Evennia's legacy inline handler from looking for the
    // legacy global client. The React socket owns submission in this client.
    event.preventDefault();
    event.stopPropagation();
    run(value);
  };

  useEffect(() => {
    const handleFunctionKey = (event: KeyboardEvent) => {
      const slot = functionKeyIndex(event.key);
      if (
        slot === null ||
        !characterResources?.character ||
        secretInput ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey ||
        event.repeat
      ) return;
      const action = hotbarActions[slot];
      if (!action) return;
      event.preventDefault();
      event.stopPropagation();
      run(action.command);
    };
    window.addEventListener("keydown", handleFunctionKey, { capture: true });
    return () => window.removeEventListener("keydown", handleFunctionKey, { capture: true });
  }, [characterResources?.character, hotbarActions, secretInput, selectedTarget, sendCommand]);

  const toggleMap = () => {
    const visible = !mapVisible;
    setMapVisible(visible);
    localStorage.setItem(MAP_VISIBLE_KEY, String(visible));
  };
  const statusColor = status === "connected" ? "success" : status === "connecting" ? "warning" : "error";

  return (
    <ThemeProvider theme={theme}>
      <style>{EVENNIA_COLOR_CSS}</style>
      <CssBaseline />
      <Box className={`app-shell ${mapVisible && !accessibility?.screenreader ? "with-map" : "without-map"}${accessibility?.screenreader ? " accessibility-screenreader" : ""}`}>
        <RoomEffects sync={accessibility?.room_effects ? roomEffects : null} />
        <Paper square elevation={0} className="topbar">
          <Stack direction="row" sx={{ alignItems: "center" }} spacing={1.5} className="brand">
            <span className="brand-mark">Q</span>
            <Box>
              <Typography variant="h6" sx={{ lineHeight: 1 }}>{config.gameName}</Typography>
              <Typography variant="caption" color="text.secondary">Journey beyond the infinite</Typography>
            </Box>
          </Stack>
          <Stack direction="row" sx={{ alignItems: "center" }} spacing={1}>
            <Chip size="small" color={statusColor} variant="outlined" label={status} />
            <Tooltip title={audioEnabled ? "Mute sound" : "Enable sound"}>
              <IconButton
                aria-label={audioEnabled ? "Mute sound" : "Enable sound"}
                color={audioEnabled ? "primary" : "default"}
                onClick={toggleAudio}
              >
                {audioEnabled ? <VolumeUpRoundedIcon /> : <VolumeOffRoundedIcon />}
              </IconButton>
            </Tooltip>
            {!accessibility?.screenreader && <Tooltip title={mapVisible ? "Hide map" : "Show map"}>
              <IconButton aria-label={mapVisible ? "Hide map" : "Show map"} color={mapVisible ? "primary" : "default"} onClick={toggleMap}>
                <MapOutlinedIcon />
              </IconButton>
            </Tooltip>}
            <Tooltip title="Settings">
              <IconButton aria-label="Open settings" onClick={() => setSettingsOpen(true)}><SettingsOutlinedIcon /></IconButton>
            </Tooltip>
          </Stack>
        </Paper>

        <ResourceHud state={characterResources} />

        <Paper component="aside" square elevation={0} className="side-panel left-panel">
          <Tabs value={leftTab} onChange={(_, value) => setLeftTab(value)} variant="fullWidth">
            <Tab label="Character" /><Tab label="Gear" /><Tab label="Comms" />
          </Tabs>
          <Divider />
          <Box className="panel-content">
            {leftTab === 0 && (
              <Stack spacing={2}>
                {characterResources?.character && (
                  <Stack direction="row" spacing={1.5} className="character-identity">
                    {characterResources.character.portrait_url && (
                      <Box className="character-headshot">
                        <Box
                          component="img"
                          className={`headshot-image headshot-${characterResources.character.species}`}
                          src={characterResources.character.portrait_url}
                          alt={`${characterResources.character.name}'s portrait`}
                        />
                      </Box>
                    )}
                    <Box className="character-identity-copy">
                      <Typography variant="overline" color="text.secondary">Character</Typography>
                      <Typography variant="h6">{characterResources.character.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {[
                          `Level ${characterResources.progression?.level ?? characterResources.character.level ?? 1}`,
                          characterResources.character.species,
                          characterResources.character.gender === "neutral"
                            ? "Gender-neutral"
                            : characterResources.character.gender,
                          characterResources.character.career,
                          characterResources.character.specialization,
                        ].filter(Boolean).join(" · ")}
                      </Typography>
                    </Box>
                  </Stack>
                )}
                {!characterResources?.character && chargenPreview?.choices.length ? (
                  <Box>
                    <Typography variant="overline" color="text.secondary">Default portraits</Typography>
                    <Box className="chargen-portrait-grid">
                      {chargenPreview.choices.map((portrait) => (
                        <Box className={chargenPreview.portrait?.id === portrait.id ? "chargen-portrait selected" : "chargen-portrait"} key={portrait.id}>
                          <Box component="img" src={portrait.url} alt={portrait.label} />
                          <Typography variant="caption">{portrait.label}</Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                ) : null}
                <Box>
                  <Typography variant="overline" color="text.secondary">Current location</Typography>
                  <Typography variant="h6">{currentRoom?.name || "Not in world"}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {currentRoom?.area || "Choose or create a character to begin."}
                  </Typography>
                </Box>
                <Button variant="outlined" startIcon={<TravelExploreOutlinedIcon />} onClick={() => run("look")}>Look around</Button>
                <Button variant="outlined" onClick={() => run("who")}>Who is online</Button>
              </Stack>
            )}
            {leftTab === 1 && (
              <Stack spacing={2}>
                <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                  <Inventory2OutlinedIcon color="primary" />
                  <Typography variant="h6">Inventory ({inventory.length}/8)</Typography>
                </Stack>
                <Box className="inventory-entity-list">
                  {inventory.length ? inventory.map((item) => (
                    <Button
                      key={item.id}
                      className="inventory-entity-button"
                      onClick={(event) => openActionMenu(event, "inventory", item)}
                    >
                      <span>{item.name}</span>
                      {item.container && <small>{item.contents_count}/{item.capacity}</small>}
                    </Button>
                  )) : <Typography variant="body2" color="text.secondary">Nothing carried.</Typography>}
                </Box>
                <Divider />
                <Typography variant="overline" color="text.secondary">Equipped</Typography>
                <Box className="inventory-entity-list">
                  {equipment.length ? equipment.map((item) => (
                    <Button
                      key={item.id}
                      className="inventory-entity-button equipped"
                      onClick={(event) => openActionMenu(event, "equipment", item)}
                    >
                      <span>{item.name}</span>
                    </Button>
                  )) : <Typography variant="body2" color="text.secondary">Nothing equipped.</Typography>}
                </Box>
                <Button variant="outlined" onClick={() => run("inventory")}>Show text inventory</Button>
              </Stack>
            )}
            {leftTab === 2 && (
              <Stack spacing={2}>
                <Typography variant="body2" color="text.secondary">
                  Use Quasar's say, tell, and channel commands. Dedicated channel streams can plug into this panel later.
                </Typography>
                <Button variant="outlined" onClick={() => setCommand("say ")}>Say something</Button>
                <Button variant="outlined" onClick={() => run("channels")}>List channels</Button>
              </Stack>
            )}
          </Box>
          <NightInsects sync={accessibility?.room_effects ? roomEffects : null} />
        </Paper>

        <Box component="main" className="terminal-panel">
          <Box className="output" role="log" aria-live="polite" style={{ fontSize }} onClickCapture={runConsoleLink}>
            {entries.length === 0 && (
              <Box className="welcome-card">
                <Typography variant="h4">Opening a channel to Quasar…</Typography>
                <Typography color="text.secondary">The connection screen will appear here.</Typography>
              </Box>
            )}
            {entries.map((entry) => (
              <div key={entry.id} className={`output-entry output-${entry.kind}`} dangerouslySetInnerHTML={{ __html: entry.html }} />
            ))}
            <div ref={outputEnd} />
          </Box>
          <Paper component="form" square elevation={8} className="command-bar" onSubmit={(event) => { event.preventDefault(); submit(); }}>
            <TextField
              fullWidth autoFocus type={secretInput ? "password" : "text"} value={command}
              disabled={status !== "connected"} onChange={(event) => setCommand(event.target.value)}
              onKeyDown={(event) => {
                if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
                event.preventDefault();
                const delta = event.key === "ArrowUp" ? 1 : -1;
                const next = Math.max(0, Math.min(history.length, historyIndex + delta));
                setHistoryIndex(next);
                setCommand(next === 0 ? "" : history[history.length - next] || "");
              }}
              placeholder={secretInput ? "Password" : status === "connected" ? "Enter a command…" : "Connecting…"}
              slotProps={{ htmlInput: { "aria-label": secretInput ? "Password" : "Game command", autoComplete: secretInput ? "current-password" : "off" } }}
            />
            <IconButton type="submit" color="primary" size="large" aria-label="Send command" disabled={!command.trim() || status !== "connected"}>
              <SendRoundedIcon />
            </IconButton>
          </Paper>
          <Paper square elevation={8} className="command-hotbar" aria-label="Adaptive command hotbar">
            {hotbarActions.map((action, index) => (
              <Tooltip key={`${index}-${action.command}`} title={action.command} placement="top">
                <Button
                  className="hotbar-button"
                  disabled={status !== "connected" || !characterResources?.character}
                  onClick={() => run(action.command)}
                >
                  <kbd>F{index + 1}</kbd>
                  <span>{action.label}</span>
                </Button>
              </Tooltip>
            ))}
          </Paper>
        </Box>

        {mapVisible && !accessibility?.screenreader && (
          <Paper component="aside" square elevation={0} className="map-panel">
            <Box className="map-pane">
              <Box className="map-heading">
                <Box>
                  <Typography variant="subtitle1">{currentRoom?.name || "Navigation"}</Typography>
                  <Typography variant="caption" color="text.secondary">{currentRoom?.area || "No location fix"}</Typography>
                </Box>
              </Box>
              <WorldMap rooms={rooms} currentId={currentRoomId} onMove={run} />
            </Box>
            <Box className="context-pane">
              <Tabs value={rightTab} onChange={(_, value) => setRightTab(value)} variant="fullWidth">
                <Tab label="Room" /><Tab label="Quests" /><Tab label="Tasks" />
              </Tabs>
              <Divider />
              <Box className="context-content">
                {rightTab === 0 && (
                  currentRoom ? <Stack spacing={1.5}>
                    <Typography variant="subtitle1" className="room-panel-title">{currentRoom.name}</Typography>
                    <Typography className="room-description">{currentRoom.description || "No description is available."}</Typography>
                    <Divider />
                    <EntityLine
                      label="Items"
                      entities={currentRoom.items}
                      tone="item"
                      onSelect={(event, item) => openActionMenu(event, "room-item", item)}
                    />
                    <EntityLine
                      label="Players"
                      entities={currentRoom.players}
                      tone="player"
                      onSelect={(event, player) => openActionMenu(event, "player", player)}
                    />
                    <EntityLine
                      label="NPCs"
                      entities={currentRoom.npcs}
                      tone="npc"
                      selectedId={selectedTargetId}
                      onSelect={(event, target) => openActionMenu(event, "npc", target)}
                    />
                  </Stack> : <Typography color="text.secondary">No room information available.</Typography>
                )}
                {rightTab === 1 && <JournalList entries={journal?.quests || []} kind="quest" run={run} />}
                {rightTab === 2 && <JournalList entries={journal?.tasks || []} kind="task" run={run} />}
              </Box>
            </Box>
          </Paper>
        )}
      </Box>

      <Menu
        open={Boolean(actionMenu)}
        onClose={() => setActionMenu(null)}
        anchorReference="anchorPosition"
        anchorPosition={actionMenu ? { top: actionMenu.y, left: actionMenu.x } : undefined}
      >
        {actionMenu && [
          ...(actionMenu.context === "npc" ? [{
            label: selectedTargetId === String(actionMenu.entity.id) ? "Clear Target" : "Target",
            command: "",
          }] : []),
          ...contextActions(actionMenu.context, actionMenu.entity, backpack),
        ].map((action) => (
          <MenuItem
            key={`${action.label}-${action.command}`}
            onClick={() => {
              if (action.command) run(action.command);
              else setSelectedTargetId((current) => (
                current === String(actionMenu.entity.id) ? null : String(actionMenu.entity.id)
              ));
              setActionMenu(null);
            }}
          >
            {action.label}
          </MenuItem>
        ))}
      </Menu>

      <Drawer anchor="right" open={settingsOpen} onClose={() => setSettingsOpen(false)}>
        <Box className="settings-drawer" role="presentation">
          <Typography variant="h5">Client settings</Typography>
          <Box>
            <Typography gutterBottom>Transcript size: {fontSize}px</Typography>
            <Slider min={12} max={22} value={fontSize} onChange={(_, value) => {
              const size = value as number;
              setFontSize(size);
              localStorage.setItem(FONT_SIZE_KEY, String(size));
            }} />
          </Box>
          <Divider />
          <Box>
            <Typography variant="h6">Sound</Typography>
            <Typography variant="body2" color="text.secondary">
              Music, station ambience, and gameplay effects are mixed separately on this device.
            </Typography>
          </Box>
          {(["master", "music", "ambience", "effects"] as const).map((channel) => (
            <Box key={channel}>
              <Typography gutterBottom sx={{ textTransform: "capitalize" }}>
                {channel}: {Math.round(audioSettings[channel] * 100)}%
              </Typography>
              <Slider
                min={0}
                max={1}
                step={0.01}
                value={audioSettings[channel]}
                onChange={(_, value) => updateAudioSetting(channel, value as number)}
                aria-label={`${channel} volume`}
              />
            </Box>
          ))}
          <Button
            startIcon={audioEnabled ? <VolumeOffRoundedIcon /> : <VolumeUpRoundedIcon />}
            variant={audioEnabled ? "outlined" : "contained"}
            onClick={toggleAudio}
          >
            {audioEnabled ? "Mute sound" : "Enable sound"}
          </Button>
          <Button startIcon={<MapOutlinedIcon />} variant="outlined" onClick={toggleMap}>{mapVisible ? "Hide map" : "Show map"}</Button>
          <Button color="warning" variant="outlined" onClick={() => run("map reset")}>Reset explored map</Button>
          <Button startIcon={<RefreshOutlinedIcon />} variant="outlined" onClick={reconnect}>Reconnect</Button>
          <Divider />
          <Button href="/webclient/legacy/" color="inherit">Open legacy client</Button>
        </Box>
      </Drawer>
    </ThemeProvider>
  );
}
