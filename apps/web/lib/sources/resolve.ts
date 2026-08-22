/** Map rule-result data_source refs to officer-clickable verification URLs. */

export type SourceLink = {
  /** Monospace label shown in the UI (source_id · snapshot). */
  label: string;
  /** Platform the check verified against (Yahoo Finance, OpenSanctions, …). */
  platform: string | null;
  /** Public page for that verification platform; null when demo/local-only. */
  url: string | null;
};

type DataSourceInput = {
  source_id: string;
  version?: string | null;
  snapshot_id?: string | null;
};

function yahooQuoteUrl(snapshotId: string | null | undefined): string | null {
  if (!snapshotId) return "https://finance.yahoo.com/";
  const m = snapshotId.match(/^yahoo:(.+)$/i);
  if (m?.[1]) {
    return `https://finance.yahoo.com/quote/${encodeURIComponent(m[1])}`;
  }
  return "https://finance.yahoo.com/";
}

/**
 * Resolve a clickable verification URL for a data source.
 * Never invent a live registry URL for DEMO/MOCK or local-only indexes.
 */
export function resolveSourceLink(ds: DataSourceInput): SourceLink {
  const id = (ds.source_id || "").toLowerCase();
  const snap = ds.snapshot_id || ds.version || null;
  const label = [ds.source_id, snap].filter(Boolean).join(" · ");

  if (id === "yahoo-finance-futures" || id === "live-market-futures") {
    return {
      label,
      platform: "Yahoo Finance",
      url: yahooQuoteUrl(ds.snapshot_id),
    };
  }

  if (id === "opensanctions") {
    return {
      label,
      platform: "OpenSanctions",
      url: "https://www.opensanctions.org/",
    };
  }

  if (id.includes("gleif")) {
    const lei = snap?.match(/[0-9A-Z]{20}/)?.[0];
    return {
      label,
      platform: "GLEIF",
      url: lei
        ? `https://search.gleif.org/#/record/${lei}`
        : "https://search.gleif.org/",
    };
  }

  if (id.includes("demo") || id.includes("mock") || id.includes("fixture") || id.includes("static")) {
    return {
      label,
      platform: "Demo snapshot",
      url: null,
    };
  }

  if (id.includes("local") || id.includes("duplicate")) {
    return {
      label,
      platform: "Local index",
      url: null,
    };
  }

  return { label, platform: null, url: null };
}

export function resolveSourceLinks(sources: DataSourceInput[]): SourceLink[] {
  if (!sources.length) return [];
  return sources.map(resolveSourceLink);
}

/** Best-effort parse of legacy "id · snap | id2 · snap2" strings from demo mode. */
export function parseLegacySourceString(source: string): SourceLink[] {
  if (!source.trim()) return [];
  return source.split("|").map((part) => {
    const bits = part.split("·").map((s) => s.trim()).filter(Boolean);
    const source_id = bits[0] || part.trim();
    const snapshot_id = bits[1] || null;
    return resolveSourceLink({ source_id, snapshot_id });
  });
}
