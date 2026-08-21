export function StatusStrip({
  documents,
  corridor,
  hsCode,
  state,
}: {
  documents: number;
  corridor: string;
  hsCode: string;
  state: string;
}) {
  const cells = [
    { label: "DOCUMENTS", value: `${documents} / 5` },
    { label: "CORRIDOR", value: corridor },
    { label: "HS CODE", value: hsCode },
    { label: "STATE", value: state },
  ];

  return (
    <div className="hairline-t hairline-b flex flex-wrap divide-x divide-rule">
      {cells.map((c) => (
        <div key={c.label} className="flex items-baseline gap-3 px-5 py-3">
          <span className="text-label text-slate">{c.label}</span>
          <span className="text-data text-ink">{c.value}</span>
        </div>
      ))}
    </div>
  );
}
