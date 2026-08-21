import type { FieldRow } from "@/content/documents";

export function FieldGrid({ rows }: { rows: FieldRow[] }) {
  return (
    <dl className="hairline-t">
      {rows.map((row) => (
        <div
          key={row.label}
          className="hairline-b grid grid-cols-[minmax(140px,26%)_1fr] gap-4 px-1 py-3"
        >
          <dt className="text-label text-slate">{row.label}</dt>
          <dd className="text-data text-ink">{row.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function DocTable({
  headers,
  rows,
}: {
  headers: readonly string[];
  rows: readonly (readonly string[])[];
}) {
  return (
    <table className="w-full border-collapse border border-rule">
      <thead>
        <tr>
          {headers.map((h) => (
            <th
              key={h}
              scope="col"
              className="text-label border border-rule px-3 py-2 text-left text-slate"
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.join("|")}>
            {row.map((cell, i) => (
              <td key={i} className="text-data border border-rule px-3 py-3 align-top text-ink">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
