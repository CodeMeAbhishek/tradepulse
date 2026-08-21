import type { DocumentKind } from "@/types";
import { blDoc, coDoc, invoiceDoc, mt700Doc } from "@/content/documents";
import { RubberStamp } from "./facsimile/RubberStamp";
import { DocTable, FieldGrid } from "./facsimile/FieldGrid";
import { cn } from "@/lib/utils";

type Meta = { label: string; value: string };

function Letterhead({
  name,
  address,
  meta,
  title,
}: {
  name: string;
  address: string[];
  meta: Meta[];
  title: string;
}) {
  return (
    <header className="hairline-b flex flex-wrap items-start justify-between gap-8 pb-6">
      <div>
        <p className="text-h3 font-mono text-ink">{name}</p>
        {address.map((line) => (
          <p key={line} className="text-small text-slate">
            {line}
          </p>
        ))}
        <p className="text-label mt-4 text-ink">{title}</p>
      </div>
      <dl className="min-w-[220px]">
        {meta.map((m) => (
          <div key={m.label} className="flex justify-between gap-6">
            <dt className="text-label text-slate">{m.label}</dt>
            <dd className="text-data text-ink">{m.value}</dd>
          </div>
        ))}
      </dl>
    </header>
  );
}

function SignatureLine({ caption }: { caption: string }) {
  return (
    <div className="mt-12 max-w-[52%]">
      <div className="h-px w-full bg-ink" />
      <p className="text-label mt-2 text-slate">{caption}</p>
    </div>
  );
}

function InvoiceBody() {
  return (
    <>
      <FieldGrid rows={invoiceDoc.parties} />
      <div className="mt-8">
        <DocTable headers={invoiceDoc.lineHeaders} rows={invoiceDoc.lines} />
      </div>
      <p className="text-data mt-6 text-ink">TOTAL {invoiceDoc.total}</p>
      <SignatureLine caption={invoiceDoc.signature} />
    </>
  );
}

function BlBody() {
  return (
    <>
      <FieldGrid rows={blDoc.parties} />
      <div className="mt-8">
        <DocTable headers={blDoc.cargoHeaders} rows={blDoc.cargo} />
      </div>
      <p className="text-label mt-6 text-ink">{blDoc.notation}</p>
      <SignatureLine caption={blDoc.signature} />
    </>
  );
}

function CoBody() {
  return (
    <>
      <FieldGrid rows={coDoc.boxes} />
      <p className="text-small mt-8 max-w-[60ch] text-slate">{coDoc.declaration}</p>
      <SignatureLine caption={coDoc.signature} />
    </>
  );
}

function Mt700Body() {
  return (
    <>
      <FieldGrid rows={mt700Doc.parties} />
      <div className="hairline-t mt-8">
        {mt700Doc.tags.map((t) => (
          <div
            key={t.tag}
            className="hairline-b grid grid-cols-[64px_minmax(140px,22%)_1fr] gap-4 py-3"
          >
            <span className="text-data text-ink">{t.tag}</span>
            <span className="text-label pt-1 text-slate">{t.label}</span>
            <span className="text-data whitespace-pre-wrap text-ink">{t.value.join("\n")}</span>
          </div>
        ))}
      </div>
      <SignatureLine caption={mt700Doc.signature} />
    </>
  );
}

const variants = {
  invoice: { doc: invoiceDoc, Body: InvoiceBody },
  packingList: { doc: invoiceDoc, Body: InvoiceBody },
  billOfLading: { doc: blDoc, Body: BlBody },
  certificateOfOrigin: { doc: coDoc, Body: CoBody },
  mt700: { doc: mt700Doc, Body: Mt700Body },
} as const;

/** Paper plane. Used wherever a normal site would put a photograph. */
export function DocumentFacsimile({
  variant,
  className,
}: {
  variant: DocumentKind;
  className?: string;
}) {
  const { doc, Body } = variants[variant];

  return (
    <article
      className={cn("relative border border-rule bg-paper px-10 py-9", className)}
      style={{ borderRadius: "2px" }}
    >
      <Letterhead
        name={doc.letterhead}
        address={[...doc.address]}
        meta={[...doc.meta]}
        title={doc.title}
      />
      <div className="mt-6">
        <Body />
      </div>
      <RubberStamp lines={[...doc.stamp]} />
    </article>
  );
}
