import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  useRouterState,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";
import { TopBar } from "../components/shell/TopBar";
import { LedgerRail } from "../components/shell/LedgerRail";
import { Footer } from "../components/shell/Footer";
import { DUR, EASE } from "../lib/motion";

const RAIL_FALLBACK: Record<string, { number: string; name: string }> = {
  "/": { number: "01", name: "HERO" },
  "/product": { number: "01", name: "THE BENCH" },
  "/method": { number: "01", name: "ARCHITECTURE" },
};

function NotFoundComponent() {
  return (
    <div className="px-6 py-[180px] lg:pl-[104px]">
      <p className="text-label text-slate">404 · NO SUCH PAGE</p>
      <h1 className="text-h1 mt-6 max-w-[30ch] font-mono text-ink">
        Nothing is filed under that reference.
      </h1>
      <p className="text-body mt-6 max-w-[54ch] text-slate">
        The page has been moved or never existed. The examination bench is at /product and the
        technical note is at /method.
      </p>
      <a href="/" className="text-label mt-10 inline-block border border-ink px-5 py-3 text-ink">
        RETURN TO THE INDEX →
      </a>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);

  return (
    <div className="px-6 py-[180px] lg:pl-[104px]">
      <p className="text-label text-slate">THIS PAGE DID NOT LOAD</p>
      <h1 className="text-h1 mt-6 max-w-[30ch] font-mono text-ink">
        Something failed on our side.
      </h1>
      <div className="mt-10 flex flex-wrap gap-4">
        <button
          onClick={() => {
            router.invalidate();
            reset();
          }}
          className="text-label border border-ink px-5 py-3 text-ink"
        >
          TRY AGAIN →
        </button>
        <a href="/" className="text-label border border-rule px-5 py-3 text-slate">
          RETURN TO THE INDEX →
        </a>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "TradePulse AI — verification middleware for trade finance" },
      {
        name: "description",
        content:
          "TradePulse examines cross-border trade document sets against UCP 600 and unit-value bands, and returns a scored exception report with every finding traced to its source.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@400;600&display=swap",
      },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <QueryClientProvider client={queryClient}>
      <TopBar />
      <LedgerRail fallback={RAIL_FALLBACK[pathname] ?? { number: "01", name: "TRADEPULSE" }} />
      <AnimatePresence mode="wait" initial={false}>
        <motion.main
          key={pathname}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: DUR.routeChange, ease: EASE.out }}
          className="lg:px-[72px]"
        >
          {/* Required: nested routes render here. Removing <Outlet /> breaks all child routes. */}
          <Outlet />
        </motion.main>
      </AnimatePresence>
      <Footer />
    </QueryClientProvider>
  );
}
