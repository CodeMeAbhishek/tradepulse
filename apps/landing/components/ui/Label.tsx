/**
 * Mono microcopy with a small filled square in front of it. The marker is what
 * makes a label read as part of a system rather than as a stray caption, and
 * it anchors a panel whose remaining space is deliberately empty.
 */
export function Label({
  children,
  tone = "ink",
  className = "",
}: {
  children: React.ReactNode;
  tone?: "ink" | "onInk" | "signal";
  className?: string;
}) {
  const color =
    tone === "onInk" ? "text-mute-on-ink" : tone === "signal" ? "text-signal" : "text-mute";
  return (
    <p className={`type-label flex items-center gap-2.5 ${color} ${className}`}>
      <span aria-hidden className="h-1.5 w-1.5 shrink-0 bg-current" />
      {children}
    </p>
  );
}
