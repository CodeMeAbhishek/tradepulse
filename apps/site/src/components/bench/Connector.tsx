import { motion } from "motion/react";
import { DUR, EASE } from "@/lib/motion";

export type Point = { x: number; y: number };

/** Drawn between two conflicting values, with a dot travelling along it. */
export function Connector({
  from,
  to,
  color,
  reduced,
}: {
  from: Point;
  to: Point;
  color: string;
  reduced: boolean;
}) {
  const midY = (from.y + to.y) / 2;
  const d = `M ${from.x} ${from.y} C ${from.x - 80} ${midY}, ${to.x - 80} ${midY}, ${to.x} ${to.y}`;

  return (
    <svg className="pointer-events-none absolute inset-0 h-full w-full" aria-hidden>
      <motion.path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={1}
        initial={{ pathLength: reduced ? 1 : 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: reduced ? 0 : DUR.connector, ease: EASE.inOut }}
      />
      {reduced ? null : (
        <motion.circle
          r={3}
          fill={color}
          initial={{ offsetDistance: "0%" }}
          animate={{ offsetDistance: "100%" }}
          transition={{ duration: DUR.connector, ease: EASE.inOut }}
          style={{ offsetPath: `path("${d}")`, offsetRotate: "0deg" }}
        />
      )}
    </svg>
  );
}
