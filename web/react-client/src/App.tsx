import { useEffect, useMemo, useRef, useState } from "react";
import {
  Box, Button, Chip, CssBaseline, Divider, Drawer, IconButton, Paper, Slider, Stack,
  Tab, Tabs, TextField, ThemeProvider, Tooltip, Typography, createTheme,
} from "@mui/material";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import MapOutlinedIcon from "@mui/icons-material/MapOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import TravelExploreOutlinedIcon from "@mui/icons-material/TravelExploreOutlined";

import { ansiToHtml, looksLikePasswordPrompt } from "./ansi";
import { hydrateMap, updateMap } from "./mapStore";
import type { ClientConfig, MapSync, MappedRoom, OutputEntry, RoomInfo } from "./types";
import { useEvenniaSocket } from "./useEvenniaSocket";
import { WorldMap } from "./WorldMap";

const MAX_OUTPUT_ENTRIES = 500;
const MAP_VISIBLE_KEY = "quasar.react.mapper.visible.v1";
const FONT_SIZE_KEY = "quasar.react.font-size.v1";

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

export default function App({ config }: AppProps) {
  const [entries, setEntries] = useState<OutputEntry[]>([]);
  const [rooms, setRooms] = useState<Record<string, MappedRoom>>({});
  const [currentRoomId, setCurrentRoomId] = useState<string | null>(null);
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [secretInput, setSecretInput] = useState(false);
  const [leftTab, setLeftTab] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mapVisible, setMapVisible] = useState(
    () => localStorage.getItem(MAP_VISIBLE_KEY) !== "false",
  );
  const [fontSize, setFontSize] = useState(
    () => Number(localStorage.getItem(FONT_SIZE_KEY) || 15),
  );
  const nextId = useRef(1);
  const outputEnd = useRef<HTMLDivElement | null>(null);
  const currentRoomIdRef = useRef<string | null>(null);

  const append = (text: string, kind: OutputEntry["kind"] = "text") => {
    if (!text) return;
    setEntries((current) => [
      ...current.slice(-(MAX_OUTPUT_ENTRIES - 1)),
      newEntry(nextId.current++, text, kind),
    ]);
    if (looksLikePasswordPrompt(text)) setSecretInput(true);
  };

  const handlers = useMemo(
    () => ({
      onText: (text: string) => append(text, "text"),
      onPrompt: (text: string) => append(text, "prompt"),
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
      onProtocol: (_name: string, _data: unknown) => undefined,
    }),
    [],
  );
  const { status, sendCommand, reconnect } = useEvenniaSocket(config, handlers);

  useEffect(() => {
    outputEnd.current?.scrollIntoView({ block: "end" });
  }, [entries]);

  useEffect(() => {
    // The old keys contained one map shared by every character. Since their
    // ownership is unknowable, discard them rather than migrate bad data.
    localStorage.removeItem("quasar.react.mapper.rooms.v1");
    localStorage.removeItem("quasar.react.mapper.rooms.v2");
  }, []);

  const submit = () => {
    const value = command.trim();
    if (!value || !sendCommand(value)) return;
    if (!secretInput) {
      append(`> ${value}`, "command");
      setHistory((current) => [...current.filter((item) => item !== value), value].slice(-100));
    }
    setHistoryIndex(0);
    setCommand("");
    setSecretInput(false);
  };

  const run = (value: string) => {
    if (!sendCommand(value)) return;
    append(`> ${value}`, "command");
  };

  const toggleMap = () => {
    const visible = !mapVisible;
    setMapVisible(visible);
    localStorage.setItem(MAP_VISIBLE_KEY, String(visible));
  };
  const currentRoom = currentRoomId ? rooms[currentRoomId] : undefined;
  const statusColor = status === "connected" ? "success" : status === "connecting" ? "warning" : "error";

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box className={`app-shell ${mapVisible ? "with-map" : "without-map"}`}>
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
            <Tooltip title={mapVisible ? "Hide map" : "Show map"}>
              <IconButton aria-label={mapVisible ? "Hide map" : "Show map"} color={mapVisible ? "primary" : "default"} onClick={toggleMap}>
                <MapOutlinedIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton aria-label="Open settings" onClick={() => setSettingsOpen(true)}><SettingsOutlinedIcon /></IconButton>
            </Tooltip>
          </Stack>
        </Paper>

        <Paper component="aside" square elevation={0} className="side-panel left-panel">
          <Tabs value={leftTab} onChange={(_, value) => setLeftTab(value)} variant="fullWidth">
            <Tab label="Character" /><Tab label="Gear" /><Tab label="Comms" />
          </Tabs>
          <Divider />
          <Box className="panel-content">
            {leftTab === 0 && (
              <Stack spacing={2}>
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
                <Inventory2OutlinedIcon color="primary" fontSize="large" />
                <Typography variant="body2" color="text.secondary">
                  Inventory output appears in the main transcript until structured character data is added.
                </Typography>
                <Button variant="contained" onClick={() => run("inventory")}>Check inventory</Button>
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
        </Paper>

        <Box component="main" className="terminal-panel">
          <Box className="output" role="log" aria-live="polite" style={{ fontSize }}>
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
        </Box>

        {mapVisible && (
          <Paper component="aside" square elevation={0} className="map-panel">
            <Box className="map-heading">
              <Box>
                <Typography variant="subtitle1">{currentRoom?.name || "Navigation"}</Typography>
                <Typography variant="caption" color="text.secondary">{currentRoom?.area || "No location fix"}</Typography>
              </Box>
            </Box>
            <WorldMap rooms={rooms} currentId={currentRoomId} onMove={run} />
          </Paper>
        )}
      </Box>

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
