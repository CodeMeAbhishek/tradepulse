import {
  CASE_STATE_DISPLAY,
  riskRouteDisplay,
  type QueueCaseRow,
} from "@/lib/contracts/mirror";
import { DataLabelBadge, FreshnessChip } from "@/components/queue/StatusChips";
import styles from "./QueueTable.module.css";

function formatSla(iso: string | null): string {
  if (iso == null) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZoneName: "short",
  }).format(date);
}

export function QueueTable({ rows }: { rows: QueueCaseRow[] }) {
  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <caption className="sr-only">
          Compliance workbench case queue from typed synthetic mocks
        </caption>
        <thead>
          <tr>
            <th scope="col">Case</th>
            <th scope="col">Parties / corridor</th>
            <th scope="col">Status</th>
            <th scope="col">Risk route</th>
            <th scope="col">Reason</th>
            <th scope="col">Assignee</th>
            <th scope="col">SLA</th>
            <th scope="col">Freshness</th>
            <th scope="col">Data</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const { summary, source_freshness, freshness } = row;
            return (
              <tr key={summary.case_id}>
                <td>
                  <span className={styles.caseId}>{summary.case_id}</span>
                  <span className={styles.hint}>Case review in next sprint</span>
                </td>
                <td>
                  <div className={styles.parties}>
                    <span>{summary.seller_name}</span>
                    <span className={styles.arrow} aria-hidden>
                      →
                    </span>
                    <span>{summary.buyer_name}</span>
                  </div>
                  <div className={styles.corridor}>{summary.corridor}</div>
                </td>
                <td>{CASE_STATE_DISPLAY[summary.status]}</td>
                <td>
                  <span className={styles.route}>
                    {riskRouteDisplay(summary.risk_route)}
                  </span>
                </td>
                <td>
                  <span className={styles.reason}>
                    {summary.highest_severity_reason ?? "—"}
                  </span>
                </td>
                <td>{summary.assignee ?? "Unassigned"}</td>
                <td>
                  <time dateTime={summary.sla_due_at ?? undefined}>
                    {formatSla(summary.sla_due_at)}
                  </time>
                </td>
                <td>
                  <FreshnessChip
                    label={source_freshness}
                    asOf={freshness.as_of}
                  />
                </td>
                <td>
                  <DataLabelBadge label={summary.data_label} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
