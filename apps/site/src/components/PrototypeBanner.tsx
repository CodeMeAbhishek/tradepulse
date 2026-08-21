/**
 * Persistent prototype honesty banner — visible on every workbench screen.
 *
 * Follows the site's convention: a hairline rule and a coloured label, not a
 * tinted panel. The body copy is ink rather than amber because --amber measures
 * ~2.8:1 on paper and this is the one message on the page that must always be
 * readable.
 */
export function PrototypeBanner() {
  return (
    <aside
      className="border-b border-amber/60 bg-bench px-4 py-2.5"
      role="status"
      aria-label="Prototype data notice"
    >
      <p className="mx-auto flex max-w-6xl flex-wrap items-baseline gap-x-3 gap-y-1">
        {/* Ink, not amber: --amber measures 2.92:1 on this ground, and this is
            the one label on the page that must never be hard to read. The amber
            stays on the rule above, where contrast rules do not apply. */}
        <span className="text-label text-ink">SYNTHETIC DEMO DATA</span>
        <span className="text-sm text-slate">
          Decision support only — not a Customs portal, payment engine, or autonomous approval
          system. No live sanctions, VLEI cryptography, or ICEGATE filing in this prototype.
        </span>
      </p>
    </aside>
  );
}
