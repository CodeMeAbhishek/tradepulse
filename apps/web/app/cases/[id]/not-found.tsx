import Link from "next/link";

export default function CaseNotFound() {
  return (
    <main className="tp-card mx-auto max-w-lg p-8 text-center">
      <h1 className="text-lg font-semibold text-[var(--tp-navy)]">Case not found</h1>
      <p className="mt-2 text-sm text-[var(--tp-muted)]">
        No demo case matches this id. Reset demo data from the header if needed.
      </p>
      <Link href="/queue" className="mt-4 inline-block text-sm text-[var(--tp-accent)]">
        Return to queue
      </Link>
    </main>
  );
}
