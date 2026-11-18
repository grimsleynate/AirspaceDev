import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../static/webclient/react",
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: false,
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        entryFileNames: "assets/benben-client.js",
        chunkFileNames: "assets/[name]-[hash].js",
        assetFileNames: (assetInfo) =>
          assetInfo.names.some((name) => name.endsWith(".css"))
            ? "assets/benben-client.css"
            : "assets/[name]-[hash][extname]",
      },
    },
  },
});
