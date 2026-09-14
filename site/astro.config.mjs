import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://sachncs.github.io",
  base: "/braid",
  trailingSlash: "never",
  output: "static",
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
  },
  build: {
    inlineStylesheets: "auto",
  },
  prefetch: {
    prefetchAll: false,
    defaultStrategy: "hover",
  },
});
