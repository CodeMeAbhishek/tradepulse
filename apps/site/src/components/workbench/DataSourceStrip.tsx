import type { DataSource } from "@/lib/api/useCases";

/**
 * States where the screen's data came from.
 *
 * This is not decoration. The product rules require live, cached, mock and
 * synthetic data to be distinguishable, and a demo that silently falls back to
 * fixtures while looking identical to a live run is exactly the dishonesty
 * those rules exist to prevent.
 *
 * Colour is never the only channel here -- every state is spelled out in words.
 */
export function DataSourceStrip({
  source,
  reason,
  loading,
}: {
  source: DataSource;
  reason: string | null;
  loading: boolean;
}) {
  const live = source === "live";

  return (
    <div
      role="status"
      aria-live="polite"
      className={
        live
          ? "flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-verified/60 bg-bench px-4 py-2"
          : "flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-rule bg-bench px-4 py-2"
      }
    >
      <span className={live ? "text-label text-verified" : "text-label text-slate"}>
        {loading ? "CONTACTING API" : live ? "LIVE API DATA" : "FIXTURE DATA"}
      </span>

      <span className="text-sm text-slate">
        {live
          ? "Cases below were returned by the TradePulse API."
          : "Cases below are synthetic fixtures, not API results."}
      </span>

      {reason ? <span className="font-mono text-xs text-slate">{reason}</span> : null}
    </div>
  );
}
