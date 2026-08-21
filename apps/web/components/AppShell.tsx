"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Compliance queue" },
  { href: "/cases/case-recon-004", label: "Case workbench" },
  { href: "/regwatch", label: "RegWatch" },
] as const;

export function AppNav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-700/80 bg-slate-950/80">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3">
        <div className="min-w-0">
          <p className="text-xs uppercase tracking-[0.14em] text-slate-400">
            Bank / GIFT IFSC trade-house
          </p>
          <Link href="/" className="text-lg font-semibold tracking-tight text-slate-50">
            TradePulse Workbench
          </Link>
        </div>
        <nav className="flex flex-wrap gap-1" aria-label="Primary">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : item.href === "/regwatch"
                  ? pathname.startsWith("/regwatch")
                  : pathname.startsWith("/cases");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  active
                    ? "rounded px-3 py-1.5 text-sm font-medium bg-slate-800 text-slate-50"
                    : "rounded px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-900 hover:text-slate-50"
                }
                aria-current={active ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
