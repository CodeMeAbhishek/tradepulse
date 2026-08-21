import Link from "next/link";

export default function CaseNotFound() {
  return (
    <div className="tp-card mx-auto max-w-md p-8 text-center">
      <h1 className="text-lg font-semibold text-[var(--tp-navy)]">Case not found</h1>
      <p className="mt-2 text-sm text-[var(--tp-muted)]">
        The case id is missing from the workbench store.
      </p>
      <Link
        href="/workbench/queue"
        className="mt-4 inline-block text-sm text-[var(--tp-accent)]"
      >
        Back to queue
      </Link>
    </div>
  );
}
