import { RegWatchPanel } from "@/components/regwatch/RegWatchPanel";
import { getRegWatchEvents } from "@/lib/mock/regwatch";

export default function RegWatchPage() {
  const events = getRegWatchEvents();

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-50">RegWatch</h1>
        <p className="mt-1 max-w-2xl text-sm text-slate-400">
          Official source registry events for the prototype. Proposals are not live rule changes
          until a human approves them. Replay never overwrites prior result versions.
        </p>
      </div>
      <RegWatchPanel events={events} />
    </main>
  );
}
