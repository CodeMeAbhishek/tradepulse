import type { Metadata } from "next";
import { fontVariables } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "TradePulse — documentary trade review",
  description:
    "TradePulse reads trade documents field by field, surfaces every discrepancy with its evidence, and hands your officer a case they can defend.",
};

/** Typed explicitly rather than with Next's generated `LayoutProps`, so
 *  `npm run typecheck` passes without a build having run first. */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-palette="ink" className={`${fontVariables} antialiased`}>
      <body className="flex min-h-screen flex-col">{children}</body>
    </html>
  );
}
