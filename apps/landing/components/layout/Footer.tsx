import { BrandMark } from "@/components/brand/BrandMark";
import { Label } from "@/components/ui/Label";
import { FOOTER, LINKS, NAV } from "@/content/site";

/**
 * No privacy or terms links: those pages do not exist, and a dead link in the
 * footer is the cheapest way to look unserious.
 */
export function Footer() {
  return (
    <footer className="bg-ink text-on-ink">
      <div className="grid-page border-b border-rule-on-ink">
        <div className="panel col-span-4 lg:col-span-6">
          <a href="#top" className="inline-flex min-h-11 items-center gap-2.5" aria-label="TradePulse, back to top">
            <BrandMark className="h-6 w-6" tone="onDark" title="" />
            <span className="type-display text-lg">TradePulse</span>
          </a>
          <p className="type-body mt-8 max-w-[26ch] text-mute-on-ink">{FOOTER.blurb}</p>
        </div>

        <nav aria-label="Footer" className="panel col-span-4 border-t border-rule-on-ink lg:col-span-3 lg:border-t-0 lg:border-l lg:border-rule-on-ink">
          <Label tone="onInk">This page</Label>
          <ul className="mt-6">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="inline-flex min-h-9 items-center text-mute-on-ink transition-colors duration-200 hover:text-on-ink"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="panel col-span-4 min-w-0 border-t border-rule-on-ink lg:col-span-3 lg:border-t-0 lg:border-l lg:border-rule-on-ink">
          <Label tone="onInk">Get in touch</Label>
          <ul className="mt-6">
            <li>
              <a
                href={`mailto:${LINKS.email}`}
                className="inline-flex min-h-9 items-center break-all text-mute-on-ink transition-colors duration-200 hover:text-on-ink"
              >
                {LINKS.email}
              </a>
            </li>
            <li>
              <a
                href={LINKS.linkedin}
                target="_blank"
                rel="noreferrer"
                className="inline-flex min-h-9 items-center text-mute-on-ink transition-colors duration-200 hover:text-on-ink"
              >
                LinkedIn
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="grid-page">
        <p className="panel col-span-4 max-w-[58ch] text-sm text-mute-on-ink lg:col-span-9">
          {FOOTER.legal}
        </p>
        <p className="panel type-label col-span-4 text-mute-on-ink lg:col-span-3 lg:text-right">
          {FOOTER.copyright}
        </p>
      </div>
    </footer>
  );
}
