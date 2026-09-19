import type Lenis from "lenis";

/**
 * The page's Lenis instance, when smooth scroll is running (it is not under
 * reduced motion). Components that need to pause scrolling (the mobile menu)
 * reach it here rather than through React context, so SmoothScroll stays a
 * render-nothing component.
 */
let instance: Lenis | null = null;

export const setLenis = (lenis: Lenis | null) => {
  instance = lenis;
};

export const getLenis = () => instance;
