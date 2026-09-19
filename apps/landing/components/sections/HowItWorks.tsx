import { Shot } from "@/components/ui/Shot";
import { Label } from "@/components/ui/Label";
import { HOW } from "@/content/site";

/**
 * A genuine sequence, so it is numbered. Each step is a row split by the grid:
 * number and title on the left three columns, the screen it produces on the
 * right nine. The screenshot sticks inside its own row on desktop — CSS only,
 * so it survives reduced motion untouched.
 */
export function HowItWorks() {
  return (
    <section id="how" className="scroll-mt-14 border-b border-rule">
      <div className="grid-page border-b border-rule">
        <div className="panel col-span-4 lg:col-span-3">
          <Label>{HOW.label}</Label>
        </div>
        <div className="panel col-span-4 border-t border-rule lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule">
          <h2 className="type-display max-w-[16ch] text-[clamp(2rem,4.4vw,3.75rem)]">{HOW.title}</h2>
        </div>
      </div>

      <ol>
        {HOW.steps.map((s) => (
          <li key={s.n} className="grid-page border-b border-rule last:border-b-0">
            <div className="panel col-span-4 lg:col-span-3">
              <div className="lg:sticky lg:top-24">
                <p className="type-data text-sm text-mute">
                  {String(s.n).padStart(2, "0")} / {String(HOW.steps.length).padStart(2, "0")}
                </p>
                <h3 className="type-display mt-6 text-[clamp(1.5rem,2.4vw,2.25rem)]">{s.title}</h3>
                <p className="type-body mt-5 max-w-[26ch] text-mute">{s.body}</p>
              </div>
            </div>
            <div className="panel col-span-4 min-w-0 border-t border-rule lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule">
              <Shot shot={s.shot} caption={s.caption} sizes="(min-width: 1024px) 52rem, 100vw" />
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
