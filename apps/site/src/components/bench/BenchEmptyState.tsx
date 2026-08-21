import { site } from "@/content/site";
import { QuietButton } from "@/components/kit/QuietButton";

export function BenchEmptyState({ onLoad }: { onLoad: () => void }) {
  return (
    <div
      className="flex min-h-[520px] flex-col justify-between border border-dashed border-rule bg-paper px-10 py-10"
      style={{ borderRadius: "2px" }}
    >
      <div>
        <p className="text-label text-slate">DROP A DOCUMENT SET, OR LOAD THE SAMPLE</p>
        <p className="text-h2 mt-6 max-w-[34ch] font-mono text-ink">Nothing on the bench.</p>
        <p className="text-body mt-5 max-w-[54ch] text-slate">
          The examination runs on five document types. A real file is never required for this demo —
          the sample set is the same one used in every walkthrough.
        </p>
      </div>

      <ul className="hairline-t mt-10 flex flex-wrap gap-x-8 gap-y-3 pt-6">
        {site.documentTypes.map((t) => (
          <li key={t} className="text-label text-slate">
            {t}
          </li>
        ))}
      </ul>

      <div className="mt-10">
        <QuietButton onClick={onLoad}>Load sample document set</QuietButton>
      </div>
    </div>
  );
}
