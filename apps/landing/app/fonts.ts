import localFont from "next/font/local";
import { Fragment_Mono } from "next/font/google";

/**
 * Typography candidates for the specimen page.
 *
 * Switzer, Zodiak and Cabinet Grotesk come from Fontshare (free for commercial
 * use). The woff2 files live in app/fonts/, so nothing is fetched from a third
 * party at runtime. Once a pairing is chosen the losers get deleted, along with
 * their files.
 */

export const switzer = localFont({
  variable: "--font-switzer",
  display: "swap",
  src: [
    { path: "./fonts/switzer-400.woff2", weight: "400", style: "normal" },
    { path: "./fonts/switzer-500.woff2", weight: "500", style: "normal" },
    { path: "./fonts/switzer-600.woff2", weight: "600", style: "normal" },
    { path: "./fonts/switzer-700.woff2", weight: "700", style: "normal" },
  ],
});

export const zodiak = localFont({
  variable: "--font-zodiak",
  display: "swap",
  src: [
    { path: "./fonts/zodiak-400.woff2", weight: "400", style: "normal" },
    { path: "./fonts/zodiak-700.woff2", weight: "700", style: "normal" },
  ],
});

export const cabinet = localFont({
  variable: "--font-cabinet",
  display: "swap",
  src: [
    { path: "./fonts/cabinet-grotesk-500.woff2", weight: "500", style: "normal" },
    { path: "./fonts/cabinet-grotesk-700.woff2", weight: "700", style: "normal" },
  ],
});

export const mono = Fragment_Mono({
  variable: "--font-mono",
  weight: "400",
  subsets: ["latin"],
  display: "swap",
});

export const fontVariables = `${switzer.variable} ${zodiak.variable} ${cabinet.variable} ${mono.variable}`;
