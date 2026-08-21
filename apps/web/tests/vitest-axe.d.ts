/**
 * Register vitest-axe's matcher types with vitest's expect.
 *
 * `expect.extend(axeMatchers)` in tests/setup.ts adds the matcher at runtime;
 * this declaration is what makes `toHaveNoViolations()` type-check.
 */

import "vitest";
import type { AxeMatchers } from "vitest-axe/matchers";

declare module "vitest" {
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface Assertion<T = unknown> extends AxeMatchers {}
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface AsymmetricMatchersContaining extends AxeMatchers {}
}
