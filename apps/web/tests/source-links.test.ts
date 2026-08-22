import { describe, expect, it } from "vitest";
import { parseLegacySourceString, resolveSourceLink } from "@/lib/sources/resolve";

describe("resolveSourceLink", () => {
  it("links Yahoo futures snapshots to the quote page", () => {
    const link = resolveSourceLink({
      source_id: "yahoo-finance-futures",
      snapshot_id: "yahoo:HG=F",
    });
    expect(link.platform).toBe("Yahoo Finance");
    expect(link.url).toBe("https://finance.yahoo.com/quote/HG%3DF");
  });

  it("links OpenSanctions to the public site", () => {
    const link = resolveSourceLink({ source_id: "opensanctions", snapshot_id: "opensanctions-match@default" });
    expect(link.url).toBe("https://www.opensanctions.org/");
  });

  it("does not invent a public URL for demo watchlists", () => {
    const link = resolveSourceLink({
      source_id: "demo-mock-watchlist",
      snapshot_id: "demo-mock-watchlist@1.0.0",
    });
    expect(link.url).toBeNull();
    expect(link.platform).toBe("Demo snapshot");
  });

  it("parses legacy joined source strings", () => {
    const links = parseLegacySourceString("yahoo-finance-futures · yahoo:HG=F");
    expect(links).toHaveLength(1);
    expect(links[0].url).toContain("finance.yahoo.com/quote/");
  });
});
