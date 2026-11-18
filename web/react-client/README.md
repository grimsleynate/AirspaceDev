# Benben React web client

This is the source for Benben's default `/webclient/` interface. Vite builds it directly into Evennia's static-file tree (`web/static/webclient/react/`).

```powershell
cd web/react-client
npm install
npm run build
```

Other scripts: `npm test` (Vitest), `npm run typecheck`, and `npm run dev` for isolated UI work. The normal test path is the built client served by Evennia.

The client speaks Evennia's standard webclient WebSocket protocol: every frame is a JSON `[command, args, kwargs]` array. Game text arrives as `text` (already converted to HTML by Evennia). Structured data arrives under the name of the Python outputfunc, so `session.msg(benben_map_sync=...)` reaches the browser as `benben_map_sync`; telnet clients receive the same call as GMCP `Benben.Map.Sync` (or an MSDP variable) automatically. Requests go the other way the same way: the browser sends `["benben_map_get", [], {}]`, a telnet client sends GMCP `Benben.Map.Get`, and both reach `benben_map_get` in `server/conf/inputfuncs.py`.

Native sound uses semantic `benben_audio_scene`, `benben_audio_play`, and
`benben_audio_stop` messages (GMCP `Benben.Audio.*`). Players must enable sound in the top bar before
the browser will start playback. Music, ambience, and effects have separate
device-local volume controls. Builders can use `soundtest <name>` in game to
exercise one-shot events.

Character status uses standard `Char.Vitals`/`Char.StatusVars` GMCP (sent as
`char_vitals`/`char_statusvars`) alongside `benben_character_resources`, which
carries health, progression, combat target, inventory, and equipment for the HUD.

The audio catalog (`src/audioCatalog.ts`) maps semantic event ids to files under
`web/static/webclient/audio/`. It is currently empty. Record each new file's
creator, source, and license alongside it before committing. Gameplay code should
emit a catalog event through `world.audio` and must never refer to a media
filename or remote URL directly.

React, MUI Core, React Flow, Howler, ANSI Up, Vite, and the supporting packages selected here are MIT-licensed. Do not add MUI X Pro/Premium components without reviewing their commercial license.
