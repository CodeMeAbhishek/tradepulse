import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Mono, IBM_Plex_Sans_Condensed } from "next/font/google";
import { Providers } from "@/components/Providers";
import { Preloader } from "@/components/Preloader";
import "./globals.css";

const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

/** The third family in the design system — used only for small uppercase labels. */
const condensed = IBM_Plex_Sans_Condensed({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-ibm-plex-condensed",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TradePulse — Documentary trade trust",
  description:
    "Evidence-backed documentary trade-compliance decision support for bank and GIFT IFSC trade-house officers. Humans decide.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${sans.variable} ${mono.variable} ${condensed.variable} antialiased`}>
        <Preloader />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
