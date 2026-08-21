/** A source note kept visible so it is trivial to correct. */
export function InlineCitation({ children }: { children: React.ReactNode }) {
  return <span className="text-label border-l border-rule pl-3 text-slate">{children}</span>;
}
