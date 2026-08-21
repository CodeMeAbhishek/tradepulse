import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TradePulse Workbench",
  description:
    "Documentary trade-compliance decision support for bank and trade-house officers (prototype skeleton).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
