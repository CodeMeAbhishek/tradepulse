import Link from "next/link";

export default function CaseNotFound() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16 text-center">
      <h1 className="text-xl font-semibold text-slate-50">Case not found</h1>
      <p className="mt-2 text-sm text-slate-400">
        No synthetic queue fixture matches this case id.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block text-sm text-sky-300 underline-offset-2 hover:underline"
      >
        Return to compliance queue
      </Link>
    </main>
  );
}
