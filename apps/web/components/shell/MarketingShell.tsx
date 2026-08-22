import Link from "next/link";
import { BrandMark } from "@/components/BrandMark";

export function MarketingShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="absolute inset-x-0 top-0 z-30 border-b border-[var(--tp-line)]/60 bg-[var(--tp-bg)]/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6">
          <Link
            href="/"
            className="flex items-center gap-2.5 rounded-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--tp-brand-orange)]"
          >
            <BrandMark className="h-9 w-9" />
            <span className="font-display text-lg font-semibold tracking-tight text-[var(--tp-navy)]">
              TradePulse
            </span>
          </Link>
          <nav className="flex items-center gap-2 sm:gap-3">
            <a
              href="#how-it-works"
              className="hidden text-sm font-medium text-[var(--tp-muted)] transition hover:text-[var(--tp-navy)] sm:inline"
            >
              How it works
            </a>
            <Link href="/workbench" className="tp-btn-primary text-sm">
              Enter workbench
            </Link>
          </nav>
        </div>
      </header>
      {children}
    </div>
  );
}
