import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { MapperPreview } from "./MapperPreview";
import type { ClientConfig } from "./types";
import "./styles.css";

const root = document.getElementById("quasar-root");
if (!root) throw new Error("Quasar client root was not found.");

const config: ClientConfig = {
  gameName: root.dataset.gameName || "Quasar",
  browserSession: root.dataset.browserSession || "",
  websocketEnabled: root.dataset.websocketEnabled === "true",
  websocketUrl: root.dataset.websocketUrl || "",
  websocketPort: root.dataset.websocketPort || "4002",
};

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    {import.meta.env.DEV && new URLSearchParams(location.search).has("mapper-preview") ? (
      <MapperPreview />
    ) : (
      <App config={config} />
    )}
  </React.StrictMode>,
);
