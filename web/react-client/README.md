# Quasar React web client

This is the source for Quasar's default `/webclient/` interface. Vite builds it directly into Evennia's static-file tree.

```powershell
cd web/react-client
npm install
npm run build
```

Use `npm run dev` only for isolated UI work. The normal test path is the built client served by Evennia.

The client uses Evennia's `json.mudstandards.org` WebSocket subprotocol. Game text arrives as ANSI in binary frames; mapper and future UI data arrive as structured GMCP envelopes.

Native sound uses semantic `Quasar.Audio.Scene`, `Quasar.Audio.Play`, and
`Quasar.Audio.Stop` messages. Players must enable sound in the top bar before
the browser will start playback. Music, ambience, and effects have separate
device-local volume controls. Builders can use `soundtest <name>` in game to
exercise one-shot events.

Character status uses standard `Char.Vitals`/`Char.StatusVars` GMCP alongside
Quasar's `Quasar.Character.Resources` package. The native HUD always shows
Health and one career resource—Tech Points, Acuity, or Skill Points—and shows
Oxygen only when the server supplies it for an organic character. Synth
physiology is never inferred in the browser.

Audio source files live in `web/static/webclient/audio/`; every addition must
be entered in that directory's `LICENSES.md` before it is committed. Gameplay code should emit a
catalog event through `world.audio` and must never refer to a media filename or
remote URL directly.

React, MUI Core, React Flow, Howler, ANSI Up, Vite, and the supporting packages selected here are MIT-licensed. Do not add MUI X Pro/Premium components without reviewing their commercial license.
