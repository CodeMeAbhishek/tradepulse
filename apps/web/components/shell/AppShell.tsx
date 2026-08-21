"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDemo } from "@/lib/demo/DemoProvider";

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/queue", label: "Queue" },
  { href: "/cases/new", label: "New case" },
  { href: "/approvals", label: "Approvals" },
  { href: "/regwatch", label: "RegWatch" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { reset, seedSamples, cases, ready, mode, apiOnline, error, refresh } = useDemo();
  const pendingChecker = cases.filter((c) => c.workflow === "MAKER_APPROVED").length;

  return (
    <div className="min-h-screen">
      <div className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-950">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-3 gap-y-1">
          <span className="font-semibold">SYNTHETIC DATA</span>
          <span className="rounded border border-amber-300 bg-white/70 px-1.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide">
            {mode === "api" ? "Live API" : "Local demo"}
            {mode === "api" && apiOnline === true ? " · connected" : null}
            {mode === "api" && apiOnline === false ? " · offline" : null}
          </span>
          <span className="text-amber-900/80">
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

      <header className="border-b border-[var(--tp-line)] bg-[var(--tp-navy)] text-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.16em] text-slate-300">
              TradePulse · Documentary compliance
            </p>
            <Link href="/" className="text-lg font-semibold tracking-tight">
              Trade Trust Workbench
            </Link>
          </div>
          <nav className="flex flex-wrap gap-1" aria-label="Primary">
            {NAV.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    active
                      ? "rounded-md bg-white/15 px-3 py-1.5 text-sm font-medium"
                      : "rounded-md px-3 py-1.5 text-sm text-slate-200 hover:bg-white/10"
                  }
                  aria-current={active ? "page" : undefined}
                >
                  {item.label}
                  {item.href === "/approvals" && ready && pendingChecker > 0 ? (
                    <span className="ml-1.5 rounded-full bg-teal-400 px-1.5 text-[10px] font-bold text-slate-900">
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
              className="rounded-md border border-white/20 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10"
            >
              Refresh
            </button>
            {mode === "api" ? (
              <button
                type="button"
                onClick={() => void seedSamples()}
                className="rounded-md border border-teal-300/40 bg-teal-500/20 px-3 py-1.5 text-xs text-teal-50 hover:bg-teal-500/30"
              >
                Seed API samples
              </button>
            ) : (
              <button
                type="button"
                onClick={() => void reset()}
                className="rounded-md border border-white/20 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10"
              >
                Reset demo data
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6">{children}</div>
    </div>
  );
}
