import { motion } from "motion/react";
import { DUR, EASE } from "@/lib/motion";
import type { Region } from "@/types";

/** Four sides drawn by stroke-dashoffset, then one pulse. Never loops. */
export function AnnotationBox({
  region,
  planeW,
  planeH,
  scale,
  color,
  reduced,
  boxRef,
}: {
  region: Region;
  planeW: number;
  planeH: number;
  scale: number;
  color: string;
  reduced: boolean;
  boxRef?: (el: SVGRectElement | null) => void;
}) {
  const x = region.x * planeW;
  const y = region.y * planeH;
  const w = region.w * planeW;
  const h = region.h * planeH;
  const perimeter = 2 * (w + h);
  const stroke = Math.max(1 / scale, 0.5);

  return (
    <svg
      className="pointer-events-none absolute top-0 left-0"
      width={planeW}
      height={planeH}
      aria-hidden
    >
      <motion.rect
        ref={boxRef}
        x={x}
        y={y}
        width={w}
        height={h}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={perimeter}
        initial={{ strokeDashoffset: reduced ? 0 : perimeter, opacity: reduced ? 1 : 0.9 }}
        animate={
          reduced
            ? { strokeDashoffset: 0, opacity: 1 }
            : { strokeDashoffset: 0, opacity: [0.9, 0.35, 1] }
        }
        transition={
          reduced
            ? { duration: 0 }
            : {
                strokeDashoffset: { duration: DUR.annotation, ease: EASE.out },
                opacity: { duration: DUR.pulse, delay: DUR.annotation, times: [0, 0.5, 1] },
              }
        }
      />
    </svg>
  );
}
