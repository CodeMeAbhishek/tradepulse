import { Label } from "@/components/ui/Label";
import { FAQ } from "@/content/site";

/**
 * Obviously interactive: the whole row is the hit area, it fills on hover, and
 * a plus rotates into a minus. Native <details>, so it works with no
 * JavaScript and is keyboard-operable for free.
 */
export function Faq() {
  return (
    <section id="faq" className="scroll-mt-14 border-b border-rule">
      <div className="grid-page border-b border-rule">
        <div className="panel col-span-4 lg:col-span-3">
          <Label>{FAQ.label}</Label>
        </div>
        <div className="panel col-span-4 border-t border-rule lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule">
          <h2 className="type-display max-w-[16ch] text-[clamp(2rem,4.4vw,3.75rem)]">{FAQ.title}</h2>
        </div>
      </div>

      {FAQ.items.map((item) => (
        <details key={item.q} className="group border-b border-rule last:border-b-0">
          {/* Flex, not grid: display:grid on a <summary> makes Chrome paint a
              stray marker in the first column. The left padding matches column
              four so the rows still line up with the heading above. */}
          {/* The indent lives on the inner span, not as percentage padding on the
              <summary>: a percentage padding-left there makes Chrome paint the
              row's contents a second time, mirrored into the left margin. */}
          <summary className="relative block list-none px-5 py-7 transition-colors duration-200 group-open:bg-paper-2 hover:bg-paper-2 sm:px-8 lg:py-8 lg:pr-10 [&::-webkit-details-marker]:hidden">
            <span className="block pr-12 lg:ml-[25%]">
            <span className="type-body max-w-[34ch]">{item.q}</span>
            {/* One SVG rather than two absolutely-positioned bars: the bars
                painted a ghost copy at the start of the summary's padding box. */}
            <svg viewBox="0 0 24 24" aria-hidden className="absolute top-1/2 right-5 h-6 w-6 -translate-y-1/2 text-mute sm:right-8 lg:right-10" fill="none">
              <path d="M3 12h18" stroke="currentColor" strokeWidth="1.25" />
              <path
                d="M12 3v18"
                stroke="currentColor"
                strokeWidth="1.25"
                className="origin-center transition-transform duration-300 group-open:rotate-90"
              />
              </svg>
            </span>
          </summary>
          <div className="bg-paper-2 px-5 pb-8 sm:px-8 lg:pr-10">
            <p className="max-w-[58ch] leading-relaxed text-mute lg:ml-[25%]">{item.a}</p>
          </div>
        </details>
      ))}
    </section>
  );
}
