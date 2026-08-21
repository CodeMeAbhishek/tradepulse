import styles from "./QueueStates.module.css";

export function QueueLoading() {
  return (
    <div className={styles.panel} role="status" aria-live="polite">
      <div className={styles.pulse} />
      <p className={styles.title}>Loading compliance queue</p>
      <p className={styles.copy}>
        Fetching typed mock cases. No live registry or sanctions calls are made
        from the browser.
      </p>
    </div>
  );
}

export function QueueEmpty() {
  return (
    <div className={styles.panel} role="status">
      <p className={styles.title}>No cases in queue</p>
      <p className={styles.copy}>
        The mock fixture set is empty for this view. When the API is wired,
        ingested presentations will appear here.
      </p>
    </div>
  );
}

export function QueueError({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className={`${styles.panel} ${styles.error}`} role="alert">
      <p className={styles.title}>Unable to load queue</p>
      <p className={styles.copy}>{message}</p>
      <button type="button" className={styles.retry} onClick={onRetry}>
        Retry mock load
      </button>
    </div>
  );
}
