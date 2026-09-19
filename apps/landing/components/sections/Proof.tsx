import { Shot } from "@/components/ui/Shot";
import { Label } from "@/components/ui/Label";
import { PROOF, type Status } from "@/content/site";

/**
 * The Aspen pattern: a full-height rule splits the row, a mono label anchors
 * the left cell and the rest of it is deliberately empty, and the content
 * fills the right. The emptiness is bounded, which is what makes it read as
 * composition rather than as leftover space.
 */
const TONE: Record<Status, string> = {
  mismatch: "text-signal",
  verified: "text-ink",
  review: "text-mute",
};

function Marker({ status }: { status: Status }) {
  if (status === "verified") return <span className="h-2 w-2 shrink-0 bg-current" />;
  if (status === "review") return <span className="h-2 w-2 shrink-0 border border-current" />;
  return <span className="h-2.5 w-2.5 shrink-0 rotate-45 bg-current" />;
}

export function Proof() {
  return (
    <section id="proof" className="grid-page scroll-mt-14 border-b border-rule">
      <div className="panel col-span-4 lg:col-span-3">
        <Label>{PROOF.label}</Label>
      </div>

      <div className="panel col-span-4 min-w-0 border-t border-rule lg:col-span-9 lg:border-t-0 lg:border-l lg:border-rule">
        <h2 className="type-display max-w-[16ch] text-[clamp(2rem,4.4vw,3.75rem)]">{PROOF.title}</h2>

        <Shot
          shot={PROOF.shot}
          caption={PROOF.caption}
          priority
          sizes="(min-width: 1024px) 70rem, 100vw"
          className="mt-10 lg:mt-14"
        />

        <ul className="mt-12 grid gap-8 sm:grid-cols-3 lg:mt-16">
          {PROOF.notes.map((n) => (
            <li key={n.field}>
              <p className={`flex items-center gap-2.5 ${TONE[n.status]}`}>
                <Marker status={n.status} />
                <span className="type-label">{n.field}</span>
              </p>
              <p className="type-body mt-4 max-w-[22ch]">{n.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
