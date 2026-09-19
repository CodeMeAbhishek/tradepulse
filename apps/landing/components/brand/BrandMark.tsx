/**
 * TradePulse mark.
 *
 * Geometry copied unchanged from the team repo
 * (tradepulse/apps/web/components/BrandMark.tsx).
 *
 * `tone="onDark"` keeps every shape and the orange, and lifts only the blues:
 * the original navy #1B4F9E nearly disappears on the dark ground.
 * `tone="original"` is for light surfaces such as the paper section.
 */
const TONES = {
  original: { ring: "#1B4F9E", t: "#1B4F9E", arrow: "#2E6FB7" },
  onDark: { ring: "#4F8BE0", t: "#4F8BE0", arrow: "#6FA3EA" },
} as const;

const ORANGE = "#E9631D";

export function BrandMark({
  className,
  tone = "onDark",
  title = "TradePulse",
}: {
  className?: string;
  tone?: keyof typeof TONES;
  title?: string;
}) {
  const c = TONES[tone];
  // Pass title="" when a visible "TradePulse" wordmark sits next to the mark:
  // the SVG is then decorative and hidden from assistive tech.
  const a11y = title
    ? ({ role: "img", "aria-label": title } as const)
    : ({ "aria-hidden": true } as const);
  return (
    <svg viewBox="0 0 200 200" className={className} {...a11y}>
      {title && <title>{title}</title>}
      <path
        d="M 119.7 26.6 A 76 76 0 1 0 171.4 74"
        fill="none"
        stroke={c.ring}
        strokeWidth="15"
        strokeLinecap="round"
      />
      <path
        d="M 48 70 A 60 60 0 0 1 156.4 120.5"
        fill="none"
        stroke={ORANGE}
        strokeWidth="13"
        strokeLinecap="round"
      />
      <path d="M 55 76 H 122 V 92 H 98 V 132 H 80 V 92 H 55 Z" fill={c.t} />
      <path
        d="M 44 138 L 66 112 L 82 128 L 101 96 L 116 112 L 152 59"
        fill="none"
        stroke={ORANGE}
        strokeWidth="12"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <path d="M 177 31 L 166 69 L 141 47 Z" fill={c.arrow} />
    </svg>
  );
}
