"use client";

import { useEffect, useState, useTransition } from "react";
import {
  loadQueueMock,
  type QueueLoadState,
  type QueueMockMode,
} from "@/lib/api/cases";
import { QueueTable } from "@/components/queue/QueueTable";
import {
  QueueEmpty,
  QueueError,
  QueueLoading,
} from "@/components/queue/QueueStates";
import styles from "./QueueView.module.css";

export function QueueView() {
  const [mode, setMode] = useState<QueueMockMode>("ready");
  const [state, setState] = useState<QueueLoadState>({ status: "loading" });
  const [isPending, startTransition] = useTransition();

  function reload(nextMode: QueueMockMode = mode) {
    setState({ status: "loading" });
    startTransition(async () => {
      const result = await loadQueueMock(nextMode);
      setState(result);
    });
  }

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    void loadQueueMock(mode).then((result) => {
      if (!cancelled) setState(result);
    });
    return () => {
      cancelled = true;
    };
  }, [mode]);

  return (
    <section className={styles.section}>
      <header className={styles.header}>
        <div>
          <h1>Compliance queue</h1>
          <p className={styles.lede}>
            Typed mock cases aligned to frozen CaseSummary / CaseState /
            DataLabel / FreshnessLabel. Source freshness is a parallel mock
            field until contracts add it.
          </p>
        </div>
        <label className={styles.mode}>
          <span>Mock state</span>
          <select
            value={mode}
            onChange={(event) => {
              const next = event.target.value as QueueMockMode;
              setMode(next);
            }}
            aria-label="Queue mock state"
          >
            <option value="ready">Ready (fixture rows)</option>
            <option value="empty">Empty</option>
            <option value="error">Error</option>
          </select>
        </label>
      </header>

      {state.status === "loading" || isPending ? <QueueLoading /> : null}
      {state.status === "empty" && !isPending ? <QueueEmpty /> : null}
      {state.status === "error" && !isPending ? (
        <QueueError message={state.message} onRetry={() => reload(mode)} />
      ) : null}
      {state.status === "ready" && !isPending ? (
        <QueueTable rows={state.rows} />
      ) : null}
    </section>
  );
}
