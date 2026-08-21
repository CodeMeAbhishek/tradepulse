import { cn } from "@/lib/utils";

/** Hairline grid, mono cells, condensed-caps headers, zebra-free. */
export function DataTable({
  headers,
  rows,
  className,
  firstColumnMono = true,
}: {
  headers: readonly string[];
  rows: readonly (readonly string[])[];
  className?: string;
  firstColumnMono?: boolean;
}) {
  return (
    <div className={cn("w-full overflow-x-auto", className)}>
      <table className="w-full border-collapse border border-rule">
        <thead>
          <tr>
            {headers.map((h) => (
              <th
                key={h}
                scope="col"
                className="text-label border border-rule px-4 py-3 text-left align-bottom text-slate"
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
                <td
                  key={i}
                  className={cn(
                    "border border-rule px-4 py-3 align-top",
                    i === 0 && firstColumnMono
                      ? "text-data whitespace-nowrap text-ink"
                      : "text-small text-slate",
                  )}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
