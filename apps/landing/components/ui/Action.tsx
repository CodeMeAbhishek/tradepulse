import type { ReactNode } from "react";

/**
 * Actions are panels, not pills.
 *
 * In a block composition a button that floats as a rounded capsule reads as
 * imported from somewhere else. These fill their cell, carry a rule, and push
 * an arrow to the far edge — the pattern Aspen Search uses for its one
 * standing action. On hover the whole block inverts.
 */
const STYLES = {
  signal: "bg-signal text-on-signal hover:brightness-110",
  ink: "bg-ink text-on-ink hover:bg-ink-2",
  paper: "bg-paper text-ink hover:bg-paper-2",
  ghost: "text-ink hover:bg-ink hover:text-on-ink",
} as const;

export function Action({
  href,
  children,
  variant = "signal",
  external = false,
  className = "",
}: {
  href: string;
  children: ReactNode;
  variant?: keyof typeof STYLES;
  external?: boolean;
  className?: string;
}) {
  return (
    <a
      href={href}
      {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
      className={`group flex min-h-16 items-center justify-between gap-8 px-6 transition-colors duration-200 lg:px-8 ${STYLES[variant]} ${className}`}
    >
      <span className="type-label">{children}</span>
      <svg viewBox="0 0 22 12" aria-hidden className="h-3 w-5 shrink-0 overflow-visible" fill="none">
        <path
          d="M0 6h20M15 1l5 5-5 5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="square"
          className="transition-transform duration-200 group-hover:translate-x-1"
        />
      </svg>
    </a>
  );
}
