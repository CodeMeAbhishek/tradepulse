import Link from "next/link";
import styles from "./PrototypeBanner.module.css";

export function PrototypeBanner() {
  return (
    <aside className={styles.banner} role="status" aria-live="polite">
      <div className={styles.mark}>TradePulse AI</div>
      <p className={styles.copy}>
        Prototype environment — synthetic transaction data. Outputs are
        decision-support recommendations requiring authorised human review. Not
        authorised to approve transactions, release funds, or make definitive
        sanctions determinations.
      </p>
      <Link className={styles.link} href="/queue">
        Compliance queue
      </Link>
    </aside>
  );
}
