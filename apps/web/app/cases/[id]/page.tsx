/**
 * Empty case route — split-screen review comes in Ansh A3+.
 */
export default async function CasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-4 px-6 py-16">
      <p className="text-sm uppercase tracking-wide text-[var(--tp-muted)]">
        Case route placeholder
      </p>
      <h1 className="text-3xl font-semibold tracking-tight">Case {id}</h1>
      <p className="text-[var(--tp-muted)]">
        No document viewer, agent trace, identity drawer, or maker/checker panel yet.
      </p>
    </main>
  );
}
