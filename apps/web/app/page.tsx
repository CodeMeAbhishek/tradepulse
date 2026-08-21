import Link from "next/link";

/**
 * Empty dashboard route — queue/workbench UI comes in Ansh A1+.
 */
export default function DashboardPage() {
  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-4 px-6 py-16">
      <p className="text-sm uppercase tracking-wide text-[var(--tp-muted)]">
        TradePulse · Prototype skeleton
      </p>
      <h1 className="text-3xl font-semibold tracking-tight">Compliance workbench</h1>
      <p className="text-[var(--tp-muted)]">
        Dashboard placeholder. No case queue, document policy, or findings UI yet.
      </p>
      <Link
        className="w-fit text-[var(--tp-accent)] underline-offset-4 hover:underline"
        href="/cases/demo"
      >
        Open sample case route
      </Link>
    </main>
  );
}
