import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig, normalizePath, type UserConfig } from "vite";

import { buildSiteDataOutputs, defaultWeeksDirectory, defaultLogPath } from "./src/content/buildSiteDataOutputs.ts";

const projectRoot = path.dirname(fileURLToPath(import.meta.url));
const sourcePath = defaultLogPath;
const generatedOutputPath = path.resolve(projectRoot, "./src/generated/site-data.json");
const publicOutputPath = path.resolve(projectRoot, "./public/site-data.json");

async function rebuildSiteData() {
  return buildSiteDataOutputs(sourcePath, { generatedOutputPath, publicOutputPath, weeksDirectory: defaultWeeksDirectory });
}

export default defineConfig(async (): Promise<UserConfig & { test: { environment: string; include: string[] } }> => {
  await rebuildSiteData();

  return {
    esbuild: {
      jsx: "automatic",
      jsxImportSource: "react",
    },
    server: {
      host: "127.0.0.1",
      port: Number(process.env.LEARNING_LOG_PORT ?? "4174"),
      strictPort: true,
    },
    test: {
      environment: "node",
      include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    },
    plugins: [
      {
        name: "learning-log-content-watch",
        configureServer(server) {
          const normalizedSource = normalizePath(sourcePath);
          const normalizedWeeks = normalizePath(defaultWeeksDirectory);
          server.watcher.add([sourcePath, defaultWeeksDirectory]);
          let timer: ReturnType<typeof setTimeout> | undefined;
          let pending = Promise.resolve();

          server.watcher.on("all", (event, changedPath) => {
            const normalized = normalizePath(changedPath);
            if (!["add", "change", "unlink"].includes(event) || (normalized !== normalizedSource && !(normalized.startsWith(normalizedWeeks + "/") && normalized.endsWith(".json")))) {
              return;
            }
            clearTimeout(timer);
            timer = setTimeout(() => {
              pending = pending.then(async () => {
                try {
                  const siteData = await rebuildSiteData();
                  server.ws.send({ type: "custom", event: "learning-log-updated", data: { generatedAt: siteData.generatedAt } });
                } catch (error) {
                  server.config.logger.error(`Keeping last valid learning-log data: ${error}`);
                }
              });
            }, 200);
          });
          server.httpServer?.once("close", () => clearTimeout(timer));
        },
      },
    ],
  };
});
