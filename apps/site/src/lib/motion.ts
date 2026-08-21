// Named durations and easings. Nothing loops.

export const DUR = {
  press: 0.12,
  underline: 0.18,
  routeChange: 0.26,
  divider: 0.4,
  annotation: 0.4,
  ruleDraw: 0.5,
  connector: 0.6,
  camera: 0.7,
  counter: 1.2,
  pulse: 1.4,
} as const;

export const EASE = {
  out: [0.22, 1, 0.36, 1],
  inOut: [0.65, 0, 0.35, 1],
} as const;

export const SPRING = { type: "spring", stiffness: 90, damping: 20 } as const;
export const SPRING_SPLIT = { type: "spring", stiffness: 120, damping: 22 } as const;

export const STAGGER_LINE = 0.07;

/** Scroll reveal, once, never on scroll up. */
export const reveal = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.18 },
  transition: SPRING,
} as const;

export const revealReduced = {
  initial: { opacity: 0 },
  whileInView: { opacity: 1 },
  viewport: { once: true, amount: 0.18 },
  transition: { duration: DUR.divider },
} as const;
