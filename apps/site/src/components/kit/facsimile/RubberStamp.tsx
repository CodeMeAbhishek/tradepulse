/** Faint circular rubber-stamp mark, rotated a few degrees. */
export function RubberStamp({ lines, rotate = -7 }: { lines: string[]; rotate?: number }) {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute right-10 bottom-10 h-[128px] w-[128px] opacity-25"
      style={{ transform: `rotate(${rotate}deg)`, color: "var(--slate)" }}
    >
      <svg viewBox="0 0 128 128" className="h-full w-full">
        <circle cx="64" cy="64" r="60" fill="none" stroke="currentColor" strokeWidth="1" />
        <circle cx="64" cy="64" r="52" fill="none" stroke="currentColor" strokeWidth="1" />
        <line x1="18" y1="64" x2="110" y2="64" stroke="currentColor" strokeWidth="1" />
        <text
          x="64"
          y="52"
          textAnchor="middle"
          fill="currentColor"
          style={{ font: "600 10px var(--font-condensed)", letterSpacing: "0.1em" }}
        >
          {lines[0]}
        </text>
        <text
          x="64"
          y="82"
          textAnchor="middle"
          fill="currentColor"
          style={{ font: "600 10px var(--font-condensed)", letterSpacing: "0.1em" }}
        >
          {lines[1]}
        </text>
      </svg>
    </div>
  );
}
