/**
 * Persistent prototype honesty banner — always visible in the workbench shell.
 */
export function PrototypeBanner() {
  return (
    <aside
      className="border-b border-amber-700/40 bg-amber-950/50 px-4 py-2.5 text-sm text-amber-100"
      role="status"
      aria-label="Prototype data notice"
    >
      <p className="mx-auto flex max-w-6xl flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="font-semibold tracking-wide">SYNTHETIC DEMO DATA</span>
        <span className="text-amber-200/90">
          Decision support only — not a Customs portal, payment engine, or autonomous approval
          system. No live sanctions, VLEI cryptography, or ICEGATE filing in this prototype.
        </span>
      </p>
    </aside>
  );
}
