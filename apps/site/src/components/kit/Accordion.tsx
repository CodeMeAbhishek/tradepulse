import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { SPRING } from "@/lib/motion";

/** Hairline rows, no boxes, rotating plus/minus. */
export function Accordion({ items }: { items: readonly { q: string; a: string }[] }) {
  const [open, setOpen] = useState<string | null>(items[0]?.q ?? null);

  return (
    <div className="hairline-t">
      {items.map((item) => {
        const isOpen = open === item.q;
        return (
          <div key={item.q} className="hairline-b">
            <button
              type="button"
              aria-expanded={isOpen}
              onClick={() => setOpen(isOpen ? null : item.q)}
              className="flex w-full items-start justify-between gap-8 py-8 text-left"
            >
              <span className="text-h3 font-mono text-ink">{item.q}</span>
              <motion.span
                aria-hidden
                animate={{ rotate: isOpen ? 90 : 0 }}
                transition={SPRING}
                className="text-h3 shrink-0 font-mono text-slate"
              >
                {isOpen ? "−" : "+"}
              </motion.span>
            </button>
            <AnimatePresence initial={false}>
              {isOpen ? (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={SPRING}
                  className="overflow-hidden"
                >
                  <p className="text-body max-w-[62ch] pb-10 text-slate">{item.a}</p>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
