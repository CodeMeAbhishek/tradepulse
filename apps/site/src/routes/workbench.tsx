import { Link, Outlet, createFileRoute } from "@tanstack/react-router";

import { PrototypeBanner } from "@/components/PrototypeBanner";

/**
 * Layout for the operational workbench.
 *
 * The marketing site is a light, paper-stock surface; the workbench is the
 * application a compliance officer actually operates. The dark plane below is
 * the boundary between the two, not an inconsistency -- it signals "you have
 * left the brochure and entered the tool", and it carries the synthetic-data
 * banner on every screen inside it.
 */

const NAV = [
  { to: "/workbench", label: "Compliance queue", exact: true },
  { to: "/workbench/cases/$caseId", label: "Case workbench", params: { caseId: "case-recon-004" } },
  { to: "/workbench/regwatch", label: "RegWatch" },
] as const;

function WorkbenchLayout() {
  return (
    <div data-plane="dark" className="bg-ink text-slate-100">
      <PrototypeBanner />

      <div className="border-b border-slate-700/60">
        <nav className="mx-auto flex max-w-6xl flex-wrap gap-1 px-4 py-3" aria-label="Workbench">
          {NAV.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              // Spread rather than pass undefined: exactOptionalPropertyTypes
              // is on, so an explicit `params={undefined}` is a type error.
              {...("params" in item ? { params: item.params } : {})}
              activeOptions={{ exact: "exact" in item ? item.exact : false }}
              className="rounded px-3 py-1.5 text-sm text-slate-300 transition-colors hover:bg-slate-800/60 hover:text-slate-50"
              activeProps={{
                className: "rounded px-3 py-1.5 text-sm font-medium bg-slate-800 text-slate-50",
                "aria-current": "page",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <Outlet />
    </div>
  );
}

export const Route = createFileRoute("/workbench")({
  head: () => ({
    meta: [
      { title: "Workbench — TradePulse AI" },
      {
        name: "description",
        content:
          "Documentary trade-compliance workbench for bank and GIFT IFSC trade-house officers. Prototype running on synthetic data.",
      },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: WorkbenchLayout,
});
