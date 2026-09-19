import { Label } from "@/components/ui/Label";
import { NEVER } from "@/content/site";

/**
 * Static panels with a struck mark. Deliberately not rows on a rule, because
 * the questions below are rows on a rule and only those open — two lists that
 * look alike but behave differently is a worse fault than either being plain.
 */
export function Never() {
  return (
    <section className="border-b border-rule">
      <div className="grid-page border-b border-rule">
        <div className="panel col-span-4 lg:col-span-3">
          <Label>{NEVER.label}</Label>
        </div>
        <div className="panel col-span-4 border-t border-rule lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule">
          <h2 className="type-display max-w-[16ch] text-[clamp(2rem,4.4vw,3.75rem)]">{NEVER.title}</h2>
        </div>
      </div>

      <ul className="grid-page">
        {NEVER.items.map((item, i) => (
          <li
            key={item}
            className={`panel col-span-4 lg:col-span-6 ${i > 0 ? "border-t border-rule" : ""} ${
              i === 1 ? "lg:border-t-0 lg:border-l" : ""
            } ${i === 3 ? "lg:border-l" : ""}`}
          >
            <span aria-hidden className="block h-4 w-4 text-mute">
              <svg viewBox="0 0 12 12" fill="none" className="h-full w-full">
                <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            </span>
            <p className="type-body mt-6 max-w-[24ch]">{item}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
