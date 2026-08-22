import type { Config } from "tailwindcss";

/**
 * Colour only.
 *
 * The app already uses Tailwind palette names throughout (bg-teal-600,
 * text-slate-500, border-amber-300, and so on). Rather than editing 233 class
 * names by hand, this file redefines what those names mean, so every existing
 * class renders in the TradePulse palette without a single component changing.
 *
 * Source of truth for the values: the eight-colour design system —
 *   bench #F4F2ED · paper #FFFDF8 · ink #12202E · slate #3A4A5C
 *   rule  #D9D4CB · stamp #C1272D · amber #D68910 · verified #2D7D5A
 */

/** Warm paper neutrals at the light end, cool ink at the dark end. */
const neutral = {
  50: "oklch(0.99 0.011 90.5)", // paper
  100: "oklch(0.955 0.011 85.8)", // bench
  200: "oklch(0.867 0.011 79.6)", // rule
  300: "oklch(0.78 0.014 80)",
  400: "oklch(0.62 0.022 250)",
  500: "oklch(0.5 0.028 252)",
  600: "oklch(0.407 0.031 254.1)", // slate
  700: "oklch(0.35 0.031 252)",
  800: "oklch(0.3 0.031 251)",
  900: "oklch(0.245 0.031 249.2)", // ink
  950: "oklch(0.2 0.028 249)",
};

const amber = {
  50: "oklch(0.97 0.0259 62.9)",
  100: "oklch(0.94 0.0432 62.9)",
  200: "oklch(0.88 0.0749 62.9)",
  300: "oklch(0.8 0.1037 62.9)",
  400: "oklch(0.71 0.1296 62.9)",
  500: "oklch(0.652 0.144 62.9)", // --amber
  600: "oklch(0.53 0.144 62.9)",
  700: "oklch(0.46 0.1354 62.9)",
  800: "oklch(0.39 0.1181 62.9)",
  900: "oklch(0.32 0.0979 62.9)",
  950: "oklch(0.25 0.0778 62.9)",
};

const stamp = {
  50: "oklch(0.97 0.0331 26.5)",
  100: "oklch(0.94 0.0552 26.5)",
  200: "oklch(0.88 0.0957 26.5)",
  300: "oklch(0.8 0.1325 26.5)",
  400: "oklch(0.71 0.1656 26.5)",
  500: "oklch(0.62 0.184 26.5)",
  600: "oklch(0.494 0.184 26.5)", // --stamp
  700: "oklch(0.46 0.173 26.5)",
  800: "oklch(0.39 0.1509 26.5)",
  900: "oklch(0.32 0.1251 26.5)",
  950: "oklch(0.25 0.0994 26.5)",
};

const verified = {
  50: "oklch(0.97 0.016 158.9)",
  100: "oklch(0.94 0.0267 158.9)",
  200: "oklch(0.88 0.0463 158.9)",
  300: "oklch(0.8 0.0641 158.9)",
  400: "oklch(0.71 0.0801 158.9)",
  500: "oklch(0.62 0.089 158.9)",
  600: "oklch(0.494 0.089 158.9)", // --verified
  700: "oklch(0.46 0.0837 158.9)",
  800: "oklch(0.39 0.073 158.9)",
  900: "oklch(0.32 0.0605 158.9)",
  950: "oklch(0.25 0.0481 158.9)",
};

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-ibm-plex-sans)", "IBM Plex Sans", "Segoe UI", "sans-serif"],
        mono: ["var(--font-ibm-plex-mono)", "ui-monospace", "monospace"],
        condensed: [
          "var(--font-ibm-plex-condensed)",
          "IBM Plex Sans Condensed",
          "IBM Plex Sans",
          "sans-serif",
        ],
        // Alias for marketing/workbench headings that still use font-display.
        display: ["var(--font-ibm-plex-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        bench: "oklch(0.955 0.011 85.8)",
        paper: "oklch(0.99 0.011 90.5)",
        ink: "oklch(0.245 0.031 249.2)",
        rule: "oklch(0.867 0.011 79.6)",
        "amber-ink": "oklch(0.505 0.114 62.9)",
        "stamp-ink": "oklch(0.455 0.176 26.5)",
        "verified-ink": "oklch(0.436 0.086 158.9)",

        slate: neutral,
        gray: neutral,
        zinc: neutral,
        neutral: neutral,
        stone: neutral,
        teal: neutral,
        sky: neutral,
        blue: neutral,
        indigo: neutral,
        cyan: neutral,

        amber,
        yellow: amber,
        orange: amber,

        stamp,
        rose: stamp,
        red: stamp,

        verified,
        emerald: verified,
        green: verified,
      },
    },
  },
  plugins: [],
};

export default config;
