import { useEffect, useState } from "react";

import initialSiteData from "../generated/site-data.json";
import type { SiteData } from "../content/types";

const SITE_DATA_URL = "/site-data.json";
const REFRESH_INTERVAL_MS = 5000;
const HOT_UPDATE_EVENT = "learning-log-updated";

export function useSiteData() {
  const [siteData, setSiteData] = useState<SiteData>(initialSiteData as SiteData);

  useEffect(() => {
    let isDisposed = false;

    const refreshSiteData = async () => {
      try {
        const response = await fetch(`${SITE_DATA_URL}?t=${Date.now()}`, {
          cache: "no-store",
        });

        if (!response.ok) {
          return;
        }

        const nextSiteData = (await response.json()) as SiteData;

        if (isDisposed) {
          return;
        }

        setSiteData((currentSiteData) =>
          currentSiteData.generatedAt.localeCompare(nextSiteData.generatedAt) >= 0
            ? currentSiteData
            : nextSiteData,
        );
      } catch {
        // Keep the last successful snapshot if the browser cannot fetch a refresh.
      }
    };

    void refreshSiteData();

    const intervalId = window.setInterval(() => {
      void refreshSiteData();
    }, REFRESH_INTERVAL_MS);

    const handleFocus = () => {
      void refreshSiteData();
    };

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        void refreshSiteData();
      }
    };

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const hotContext = import.meta.hot;
    const handleHotUpdate = () => {
      void refreshSiteData();
    };

    hotContext?.on(HOT_UPDATE_EVENT, handleHotUpdate);

    return () => {
      isDisposed = true;
      window.clearInterval(intervalId);
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      hotContext?.off(HOT_UPDATE_EVENT, handleHotUpdate);
    };
  }, []);

  return siteData;
}
