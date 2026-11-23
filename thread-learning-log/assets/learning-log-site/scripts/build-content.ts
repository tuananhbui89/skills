import path from "node:path";
import { fileURLToPath } from "node:url";

import { buildSiteDataOutputs, defaultWeeksDirectory, defaultLogPath } from "../src/content/buildSiteDataOutputs.ts";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = defaultLogPath;
const generatedOutputPath = path.resolve(projectRoot, "./src/generated/site-data.json");
const publicOutputPath = path.resolve(projectRoot, "./public/site-data.json");

buildSiteDataOutputs(sourcePath, { generatedOutputPath, publicOutputPath, weeksDirectory: defaultWeeksDirectory }).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
