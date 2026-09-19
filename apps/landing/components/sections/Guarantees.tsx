import { GUARANTEES } from "@/content/site";

/**
 * Four cells tiling the row edge to edge, each holding one constraint the
 * product's code enforces. Figure and phrase finish each other, so neither
 * reads as a label stuck above a number.
 */
export function Guarantees() {
  return (
    <section aria-label="What the product guarantees" className="grid-page border-b border-rule">
      {GUARANTEES.map((g, i) => (
        <div
          key={g.label}
          className={`panel col-span-2 lg:col-span-3 ${
            i > 0 ? "border-l border-rule" : ""
          } ${i > 1 ? "border-t border-rule lg:border-t-0" : ""} ${i === 2 ? "lg:border-l" : ""}`}
        >
          <p className="type-display type-data text-[clamp(2.5rem,4.5vw,4rem)]">{g.figure}</p>
          <p className="type-body mt-5 max-w-[16ch]">{g.label}</p>
          <p className="mt-4 max-w-[24ch] text-sm leading-relaxed text-mute">{g.hint}</p>
        </div>
      ))}
    </section>
  );
}
