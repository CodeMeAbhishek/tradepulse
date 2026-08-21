import { Link } from "@tanstack/react-router";
import { cn } from "@/lib/utils";

type Variant = "solid" | "outline" | "underline";
type Tone = "ink" | "paper";

type Common = {
  children: React.ReactNode;
  className?: string;
  variant?: Variant;
  tone?: Tone;
};

const base =
  "group relative inline-flex items-center gap-3 overflow-hidden transition-[border-color,color,transform] duration-[120ms] active:translate-y-px";

/**
 * Complete class strings only — never assembled from a variable, because
 * Tailwind scans this file statically and a built-up name compiles to nothing.
 */
const styles: Record<string, string> = {
  "solid-ink": "border border-ink bg-ink px-7 py-4 text-paper",
  "solid-paper": "border border-paper bg-paper px-7 py-4 text-ink",
  "outline-ink": "border border-ink px-7 py-4 text-ink hover:border-slate",
  "outline-paper": "border border-rule px-7 py-4 text-paper hover:border-paper",
  "underline-ink": "pb-1 text-ink",
  "underline-paper": "pb-1 text-paper",
};

/** The colour the sweep paints, and the colour the label turns once covered. */
const sweep: Record<string, { fill: string; label: string }> = {
  "solid-ink": { fill: "bg-paper", label: "group-hover:text-ink" },
  "solid-paper": { fill: "bg-ink", label: "group-hover:text-paper" },
};

function Inner({ children, variant, tone }: Omit<Common, "className">) {
  const key = `${variant}-${tone}`;
  const s = sweep[key];

  return (
    <>
      {/* the fill, sweeping in from the left */}
      {s ? (
        <span
          aria-hidden
          className={cn(
            "absolute inset-0 origin-left scale-x-0 transition-transform duration-[220ms] ease-out group-hover:scale-x-100 group-focus-visible:scale-x-100",
            s.fill,
          )}
        />
      ) : null}

      <span className={cn("text-label relative z-10 transition-colors duration-[220ms]", s?.label)}>
        {children}
      </span>

      <span
        aria-hidden
        className={cn(
          "relative z-10 transition-transform duration-[220ms] ease-out group-hover:translate-x-1",
          s?.label,
        )}
      >
        →
      </span>

      {/* the hairline that draws under a text link */}
      {variant === "underline" ? (
        <span
          aria-hidden
          className="absolute bottom-0 left-0 h-px w-full origin-left scale-x-0 transition-transform duration-[180ms] group-hover:scale-x-100 group-focus-visible:scale-x-100"
          style={{ backgroundColor: tone === "ink" ? "var(--ink)" : "var(--paper)" }}
        />
      ) : null}
    </>
  );
}

export function QuietButton({
  children,
  className,
  variant = "solid",
  tone = "ink",
  onClick,
  type = "button",
}: Common & { onClick?: () => void; type?: "button" | "submit" }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={cn(base, styles[`${variant}-${tone}`], className)}
    >
      <Inner variant={variant} tone={tone}>
        {children}
      </Inner>
    </button>
  );
}

export function QuietLink({
  children,
  className,
  variant = "underline",
  tone = "ink",
  to,
}: Common & { to: string }) {
  return (
    <Link to={to as "/"} className={cn(base, styles[`${variant}-${tone}`], className)}>
      <Inner variant={variant} tone={tone}>
        {children}
      </Inner>
    </Link>
  );
}
