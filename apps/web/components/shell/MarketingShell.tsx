import Link from "next/link";

export function MarketingShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="absolute inset-x-0 top-0 z-20">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5 sm:px-6">
          <Link href="/" className="font-display text-xl font-semibold tracking-tight text-[var(--tp-navy)]">
            TradePulse
          </Link>
          <Link
            href="/workbench"
            className="text-sm font-semibold text-[var(--tp-teal)] transition hover:text-[var(--tp-navy)]"
          >
            Enter workbench
          </Link>
        </div>
      </header>
      {children}
    </div>
  );
}
