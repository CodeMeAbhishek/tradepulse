/**
 * Shared text assertions for TradePulse safety tests.
 *
 * Compliance copy deliberately names the thing it is ruling out -- e.g.
 * "outcome is explicitly NOT AVAILABLE, never PASS". A naive substring search
 * flags that correct wording as a violation, so every check here is
 * negation-aware: only an *asserted* claim counts.
 */

const NEGATORS = [
  "not",
  "never",
  "no",
  "isnt",
  "arent",
  "cannot",
  "without",
  "than",
  "neither",
];

/** How many times `phrase` appears in `haystack` as an assertion, not a denial. */
export function assertedOccurrences(haystack: string, phrase: string): number {
  const hay = haystack.toLowerCase();
  const needle = phrase.toLowerCase();
  let count = 0;
  let from = 0;
  for (;;) {
    const at = hay.indexOf(needle, from);
    if (at === -1) return count;
    const preceding = hay
      .slice(Math.max(0, at - 40), at)
      .replace(/[^a-z\s]/g, " ")
      .split(/\s+/)
      .filter(Boolean);
    if (!preceding.slice(-4).some((w) => NEGATORS.includes(w))) count += 1;
    from = at + needle.length;
  }
}

/** True when the text asserts the phrase at least once. */
export function asserts(haystack: string, phrase: string): boolean {
  return assertedOccurrences(haystack, phrase) > 0;
}
