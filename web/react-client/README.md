# Quasar React web client

This is the source for Quasar's default `/webclient/` interface. Vite builds it directly into Evennia's static-file tree.

```powershell
cd web/react-client
npm install
npm run build
```

Use `npm run dev` only for isolated UI work. The normal test path is the built client served by Evennia.

The client speaks Evennia's standard webclient WebSocket protocol: every frame is a JSON `[command, args, kwargs]` array. Game text arrives as `text` (already converted to HTML by Evennia). Structured data arrives under the name of the Python outputfunc, so `session.msg(quasar_map_sync=...)` reaches the browser as `quasar_map_sync`; telnet clients receive the same call as GMCP `Quasar.Map.Sync` (or an MSDP variable) automatically. Requests go the other way the same way: the browser sends `["quasar_map_get", [], {}]`, a telnet client sends GMCP `Quasar.Map.Get`, and both reach `quasar_map_get` in `server/conf/inputfuncs.py`.

Native sound uses semantic `quasar_audio_scene`, `quasar_audio_play`, and
`quasar_audio_stop` messages (GMCP `Quasar.Audio.*`). Players must enable sound in the top bar before
the browser will start playback. Music, ambience, and effects have separate
device-local volume controls. Builders can use `soundtest <name>` in game to
exercise one-shot events.

Character status uses standard `Char.Vitals`/`Char.StatusVars` GMCP (sent as
`char_vitals`/`char_statusvars`) alongside Quasar's `quasar_character_resources`. The native HUD always shows
Health and one career resource—Tech Points, Acuity, or Skill Points—and shows
Oxygen only when the server supplies it for an organic character. Synth
physiology is never inferred in the browser.

Audio source files live in `web/static/webclient/audio/`; every addition must
be entered in that directory's `LICENSES.md` before it is committed. Gameplay code should emit a
catalog event through `world.audio` and must never refer to a media filename or
remote URL directly.

React, MUI Core, React Flow, Howler, ANSI Up, Vite, and the supporting packages selected here are MIT-licensed. Do not add MUI X Pro/Premium components without reviewing their commercial license.
