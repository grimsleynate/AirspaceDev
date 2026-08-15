# Quasar React web client

This is the source for Quasar's default `/webclient/` interface. Vite builds it directly into Evennia's static-file tree.

```powershell
cd web/react-client
npm install
npm run build
```

Use `npm run dev` only for isolated UI work. The normal test path is the built client served by Evennia.

The client uses Evennia's `json.mudstandards.org` WebSocket subprotocol. Game text arrives as ANSI in binary frames; mapper and future UI data arrive as structured GMCP envelopes.

React, MUI Core, React Flow, ANSI Up, Vite, and the supporting packages selected here are MIT-licensed. Do not add MUI X Pro/Premium components without reviewing their commercial license.
