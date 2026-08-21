import type { Metadata } from "next";
import { IBM_Plex_Sans } from "next/font/google";
import { WorkbenchShell } from "@/components/WorkbenchShell";
import "./globals.css";

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TradePulse Workbench",
  description:
    "Documentary trade-compliance decision support for bank and GIFT IFSC trade-house officers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${ibmPlexSans.variable} min-h-screen antialiased`}>
        <WorkbenchShell>{children}</WorkbenchShell>
      </body>
    </html>
  );
}
