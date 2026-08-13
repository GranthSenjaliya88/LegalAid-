import { useMediaQuery } from "./useMediaQuery";

/** Whether the user has requested reduced motion. Gate non-essential animation on this. */
export function usePrefersReducedMotion(): boolean {
  return useMediaQuery("(prefers-reduced-motion: reduce)");
}
