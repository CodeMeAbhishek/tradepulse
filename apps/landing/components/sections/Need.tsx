import { Label } from "@/components/ui/Label";
import { NEED } from "@/content/site";

/**
 * An ink block: cited market figures, each carrying the period it refers to,
 * with the source directly underneath. These are not our metrics and the page
 * has to be unmistakable about that.
 */
export function Need() {
  return (
    <section className="border-b border-rule bg-ink text-on-ink">
      <div className="grid-page border-b border-rule-on-ink">
        <div className="panel col-span-4 lg:col-span-3">
          <Label tone="onInk">{NEED.label}</Label>
        </div>
        <div className="panel col-span-4 border-t border-rule-on-ink lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule-on-ink">
          <h2 className="type-display max-w-[18ch] text-[clamp(2rem,4.4vw,3.75rem)]">
            <span className="text-on-ink">{NEED.lead}</span>{" "}
            <span className="text-mute-on-ink">{NEED.rest}</span>
          </h2>
        </div>
      </div>

      <dl className="grid-page">
        {NEED.figures.map((f, i) => (
          <div
            key={f.label}
            className={`panel col-span-4 ${i > 0 ? "border-t border-rule-on-ink lg:border-t-0 lg:border-l" : ""}`}
          >
            <dd className="type-display type-data text-[clamp(2rem,3.4vw,2.875rem)]">{f.figure}</dd>
            <dt className="type-body mt-5 max-w-[18ch]">{f.label}</dt>
            <p className="type-label mt-4 text-mute-on-ink">{f.period}</p>
          </div>
        ))}
      </dl>

      <div className="border-t border-rule-on-ink">
        <p className="panel max-w-[62ch] text-sm leading-relaxed text-mute-on-ink">{NEED.sources}</p>
      </div>
    </section>
  );
}
