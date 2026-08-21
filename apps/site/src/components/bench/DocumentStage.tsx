import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import type { Finding } from "@/types";
import { SEVERITY_COLOR } from "@/lib/severity";
import { SPRING_SPLIT } from "@/lib/motion";
import { DocumentPane } from "./DocumentPane";
import { Connector, type Point } from "./Connector";

/** Left side of the bench. One camera move, not scattered effects. */
export function DocumentStage({ finding, reduced }: { finding: Finding | null; reduced: boolean }) {
  const [topPoint, setTopPoint] = useState<Point | null>(null);
  const [bottomPoint, setBottomPoint] = useState<Point | null>(null);

  const split = finding?.type === "cross_document";
  const color = finding ? SEVERITY_COLOR[finding.severity] : "var(--ink)";

  const onTop = useCallback((p: Point | null) => setTopPoint(p), []);
  const onBottom = useCallback((p: Point | null) => setBottomPoint(p), []);

  return (
    <div
      data-bench-stage
      className="relative h-[560px] min-w-0 overflow-hidden sm:h-[620px] lg:h-[760px] xl:h-[860px] border border-rule bg-paper"
      style={{ borderRadius: "2px" }}
    >
      <div className="flex h-full flex-col">
        <motion.div
          className="min-h-0 overflow-hidden"
          animate={{ flexGrow: 1, flexBasis: split ? "50%" : "100%" }}
          transition={reduced ? { duration: 0 } : SPRING_SPLIT}
        >
          <DocumentPane
            kind={finding?.sourceKind ?? "invoice"}
            region={finding ? finding.region : null}
            color={color}
            reduced={reduced}
            zoom={split ? 1.25 : 1.55}
            label={`${finding?.sourceDoc ?? "Commercial Invoice"} · p.${finding?.page ?? 1}`}
            onBoxPoint={onTop}
          />
        </motion.div>

        <AnimatePresence>
          {split && finding?.secondKind && finding.secondRegion ? (
            <motion.div
              key="second"
              initial={{ flexBasis: "0%", opacity: 0 }}
              animate={{ flexBasis: "50%", opacity: 1 }}
              exit={{ flexBasis: "0%", opacity: 0 }}
              transition={reduced ? { duration: 0 } : SPRING_SPLIT}
              className="min-h-0 shrink-0 overflow-hidden border-t border-rule"
            >
              <DocumentPane
                kind={finding.secondKind}
                region={finding.secondRegion}
                color={color}
                reduced={reduced}
                zoom={1.25}
                label={`${finding.secondDoc} · p.1`}
                onBoxPoint={onBottom}
              />
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>

      {split && topPoint && bottomPoint ? (
        <Connector
          key={finding?.id}
          from={topPoint}
          to={bottomPoint}
          color={color}
          reduced={reduced}
        />
      ) : null}
    </div>
  );
}
