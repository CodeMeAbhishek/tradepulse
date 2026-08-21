"use client";

import Link from "next/link";

/** Legacy dark nav — unused by current workbench routes. Prefer shell/AppShell. */
const NAV = [
  { href: "/workbench", label: "Overview" },
  { href: "/workbench/queue", label: "Queue" },
  { href: "/workbench/regwatch", label: "RegWatch" },
] as const;

export function AppNav() {
  return (
    <header className="border-b border-[var(--tp-line)] bg-[var(--tp-elevated)]">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="font-display text-lg font-semibold text-[var(--tp-navy)]">
          TradePulse
        </Link>
        <nav className="flex flex-wrap gap-1" aria-label="Primary">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-3 py-1.5 text-sm text-[var(--tp-muted)] hover:bg-slate-100"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
