import {
  DATA_LABEL_DISPLAY,
  FRESHNESS_LABEL_DISPLAY,
  type DataLabel,
  type FreshnessLabel,
} from "@/lib/contracts/mirror";
import styles from "./StatusChips.module.css";

export function DataLabelBadge({ label }: { label: DataLabel }) {
  return (
    <span className={`${styles.chip} ${styles[`data_${label}`] ?? ""}`}>
      {DATA_LABEL_DISPLAY[label]}
    </span>
  );
}

export function FreshnessChip({
  label,
  asOf,
}: {
  label: FreshnessLabel;
  asOf: string | null;
}) {
  const title =
    asOf != null
      ? `${FRESHNESS_LABEL_DISPLAY[label]} · as of ${asOf}`
      : FRESHNESS_LABEL_DISPLAY[label];

  return (
    <span
      className={`${styles.chip} ${styles[`fresh_${label}`] ?? ""}`}
      title={title}
    >
      {FRESHNESS_LABEL_DISPLAY[label]}
    </span>
  );
}
