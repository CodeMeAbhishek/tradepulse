import { Link } from "@tanstack/react-router";
import { site } from "@/content/site";

export function Footer() {
  const { footer } = site;

  return (
    <footer className="bg-ink pt-[120px] pb-10 lg:px-[72px]">
      <div className="mx-auto w-full max-w-[1600px] px-6 lg:px-10">
        <p className="text-h2 max-w-[42ch] font-mono text-paper">{footer.line}</p>

        <div className="ledger-grid mt-[96px] gap-y-10">
          {footer.columns.map((col) => (
            <div key={col.header} className="col-span-12 md:col-span-4 lg:col-span-3">
              <p className="text-label text-rule">{col.header}</p>
              <ul className="mt-5 flex flex-col gap-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      to={l.to}
                      className="group relative pb-1 text-rule transition-colors duration-[120ms] hover:text-paper"
                      style={{ fontSize: "15px" }}
                    >
                      {l.label}
                      <span
                        aria-hidden
                        className="absolute bottom-0 left-0 h-px w-full origin-left scale-x-0 bg-paper transition-transform duration-[180ms] group-hover:scale-x-100 group-focus-visible:scale-x-100"
                      />
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-[96px] flex flex-wrap justify-between gap-4 border-t border-slate pt-6">
          <span className="text-label text-slate">{footer.place}</span>
          <span className="text-label text-slate">{footer.corridor}</span>
        </div>
      </div>
    </footer>
  );
}
