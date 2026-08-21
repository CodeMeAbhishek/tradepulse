import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "motion/react";
import type { DocumentKind, Region } from "@/types";
import { DocumentFacsimile } from "@/components/kit/DocumentFacsimile";
import { AnnotationBox } from "./AnnotationBox";
import { DUR, EASE } from "@/lib/motion";

type Size = { w: number; h: number };

/**
 * One document plane with a FLIP-style camera. Every measurement happens in an
 * effect after mount, so the server and the first client paint agree.
 */
export function DocumentPane({
  kind,
  region,
  color,
  reduced,
  zoom = 1.55,
  label,
  onBoxPoint,
}: {
  kind: DocumentKind;
  region: Region | null;
  color: string;
  reduced: boolean;
  zoom?: number;
  label: string;
  onBoxPoint?: (point: { x: number; y: number } | null) => void;
}) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const planeRef = useRef<HTMLDivElement>(null);
  const boxRef = useRef<SVGRectElement | null>(null);
  const [viewport, setViewport] = useState<Size | null>(null);
  const [plane, setPlane] = useState<Size | null>(null);

  const measure = useCallback(() => {
    const vp = viewportRef.current;
    const pl = planeRef.current;
    if (!vp || !pl) return;
    // rAF one frame after any layout change, then read.
    requestAnimationFrame(() => {
      const vpRect = vp.getBoundingClientRect();
      const plRect = pl.getBoundingClientRect();
      const scaleNow = plRect.width / (pl.offsetWidth || 1);
      setViewport({ w: vpRect.width, h: vpRect.height });
      setPlane({
        w: pl.offsetWidth,
        h: plRect.height / (scaleNow || 1),
      });
    });
  }, []);

  useEffect(() => {
    measure();
    const vp = viewportRef.current;
    const pl = planeRef.current;
    if (!vp || !pl) return;
    const ro = new ResizeObserver(() => measure());
    ro.observe(vp);
    ro.observe(pl);

    // requestAnimationFrame is parked while the tab is hidden, so a bench that
    // loads in a background tab would never finish measuring. Re-measure when
    // the page comes back into view.
    const onVisible = () => {
      if (!document.hidden) measure();
    };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      ro.disconnect();
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [measure, kind]);

  const ready = viewport !== null && plane !== null;

  // At rest the whole document must be visible — a facsimile taller than the
  // pane was being clipped mid-table by the overflow. Fit it to the pane, then
  // the camera zooms past 1:1 only when a finding cites a region.
  const fit = ready && viewport && plane && plane.h > 0 ? Math.min(1, viewport.h / plane.h) : 1;
  const scale = region && ready ? zoom : fit;

  let tx = 0;
  let ty = 0;
  if (!region && ready && viewport && plane) {
    // centre the fitted page in the pane
    tx = Math.max(0, (viewport.w - plane.w * scale) / 2);
  } else if (region && ready && viewport && plane) {
    const cx = (region.x + region.w / 2) * plane.w * scale;
    const cy = (region.y + region.h / 2) * plane.h * scale;
    tx = viewport.w / 2 - cx;
    ty = viewport.h / 2 - cy;
    const minX = Math.min(0, viewport.w - plane.w * scale);
    const minY = Math.min(0, viewport.h - plane.h * scale);
    tx = Math.min(0, Math.max(minX, tx));
    ty = Math.min(0, Math.max(minY, ty));
  }

  // Report the annotation box centre in stage coordinates for the connector.
  useEffect(() => {
    if (!onBoxPoint) return;
    if (!region || !ready) {
      onBoxPoint(null);
      return;
    }
    const frame = requestAnimationFrame(() => {
      const box = boxRef.current;
      const vp = viewportRef.current;
      const stage = vp?.closest("[data-bench-stage]");
      if (!box || !stage) return;
      const b = box.getBoundingClientRect();
      const s = stage.getBoundingClientRect();
      onBoxPoint({
        x: b.left - s.left + b.width,
        y: b.top - s.top + b.height / 2,
      });
    });
    return () => cancelAnimationFrame(frame);
  }, [onBoxPoint, region, ready, tx, ty, scale]);

  return (
    <div className="relative h-full overflow-hidden bg-paper">
      <div ref={viewportRef} className="h-full w-full overflow-hidden">
        <motion.div
          ref={planeRef}
          className="relative w-full origin-top-left"
          animate={{ x: tx, y: ty, scale }}
          transition={reduced ? { duration: 0 } : { duration: DUR.camera, ease: EASE.out }}
        >
          <DocumentFacsimile variant={kind} className="border-0" />
          {region && ready && plane ? (
            <AnnotationBox
              region={region}
              planeW={plane.w}
              planeH={plane.h}
              scale={scale}
              color={color}
              reduced={reduced}
              boxRef={(el) => {
                boxRef.current = el;
              }}
            />
          ) : null}
        </motion.div>
      </div>
      <span className="text-label absolute top-0 right-0 border-b border-l border-rule bg-paper px-3 py-2 text-slate">
        {label}
      </span>
    </div>
  );
}
