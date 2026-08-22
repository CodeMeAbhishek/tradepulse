"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDemo } from "@/lib/demo/DemoProvider";
import { cn } from "@/lib/cn";
import { BrandMark } from "@/components/BrandMark";

const NAV = [
  { href: "/workbench", label: "Overview", match: "exact" as const },
  { href: "/workbench/queue", label: "Queue", match: "prefix" as const },
  { href: "/workbench/cases/new", label: "New case", match: "prefix" as const },
  { href: "/workbench/approvals", label: "Approvals", match: "prefix" as const },
  { href: "/workbench/regwatch", label: "RegWatch", match: "prefix" as const },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  /**
   * The page-in animation is replayed by re-rendering with a changing
   * animation-name, not by remounting and not by touching classList.
   *
   * Both of those were tried and both broke navigation: `key={pathname}` on
   * this wrapper makes React discard a subtree the App Router is concurrently
   * patching, and mutating className behind React's back desynchronises its
   * tree from the DOM. Either produces
   * "insertBefore / removeChild: node is not a child of this node".
   */
  const { reset, seedSamples, cases, ready, mode, apiOnline, error, refresh } = useDemo();
  const pendingChecker = cases.filter((c) => c.workflow === "MAKER_APPROVED").length;

  return (
    <div className="min-h-screen">
      <div className="border-b border-amber-200/80 bg-amber-50 px-4 py-2.5 text-sm text-amber-950">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-3 gap-y-1">
          <span className="font-semibold tracking-wide">SYNTHETIC DATA</span>
          <span className="rounded border border-amber-300/80 bg-white/80 px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide">
            {mode === "api" ? "Live API" : "Local demo"}
            {mode === "api" && apiOnline === true ? " · connected" : null}
            {mode === "api" && apiOnline === false ? " · offline" : null}
          </span>
          <span className="text-amber-900/85">
            Decision support for bank & GIFT IFSC trade-house officers — not a Customs portal,
            payment engine, or autonomous approver.
          </span>
        </div>
        {error ? (
          <div className="mx-auto mt-1 max-w-7xl text-xs text-rose-800">
            API error: {error}. Start the API on :8000 or set NEXT_PUBLIC_DATA_MODE=demo.
          </div>
        ) : null}
      </div>

      <header className="border-b border-[var(--tp-line)] bg-[var(--tp-elevated)]/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3">
          <div className="min-w-0">
            <Link href="/" className="flex items-center gap-2">
              <BrandMark className="h-8 w-8" />
              <span className="font-display text-lg font-semibold tracking-tight text-[var(--tp-navy)]">
                TradePulse
              </span>
            </Link>
            <p className="mt-0.5 pl-10 text-[11px] uppercase tracking-[0.14em] text-[var(--tp-muted)]">
              Officer workbench
            </p>
          </div>
          <nav className="flex flex-wrap gap-1" aria-label="Primary">
            {NAV.map((item) => {
              const active =
                item.match === "exact"
                  ? pathname === item.href
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "tp-nav-link cursor-pointer rounded-md px-3 py-1.5 text-sm font-medium transition-colors duration-200",
                    active
                      ? "bg-[var(--tp-navy)] text-[var(--tp-surface)]"
                      : "text-[var(--tp-muted)] hover:bg-[var(--tp-bg)] hover:text-[var(--tp-navy)]",
                  )}
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                  {item.href === "/workbench/approvals" && ready && pendingChecker > 0 ? (
                    <span className="ml-1.5 rounded bg-teal-100 px-1.5 text-[10px] font-bold text-teal-900">
                      {pendingChecker}
                    </span>
                  ) : null}
                </Link>
              );
            })}
          </nav>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void refresh()}
              className="cursor-pointer rounded-md border border-[var(--tp-line)] px-3 py-1.5 text-xs font-medium text-[var(--tp-muted)] transition hover:bg-slate-50"
            >
              Refresh
            </button>
            {mode === "api" ? (
              <button
                type="button"
                onClick={() => void seedSamples()}
                className="cursor-pointer rounded-md border border-teal-700/30 bg-teal-50 px-3 py-1.5 text-xs font-medium text-teal-900 transition hover:bg-teal-100"
              >
                Seed API samples
              </button>
            ) : (
              <button
                type="button"
                onClick={() => void reset()}
                className="cursor-pointer rounded-md border border-[var(--tp-line)] px-3 py-1.5 text-xs font-medium text-[var(--tp-muted)] transition hover:bg-slate-50"
              >
                Reset demo data
              </button>
            )}
          </div>
        </div>
      </header>

      <div data-route={pathname} className="tp-route mx-auto max-w-7xl px-4 py-6">
        {children}
      </div>
    </div>
  );
}
