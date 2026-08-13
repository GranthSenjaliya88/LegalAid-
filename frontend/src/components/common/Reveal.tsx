import { type ReactNode } from "react";
import { motion, type Variants } from "framer-motion";
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion";
import { cn } from "@/lib/utils";

interface RevealProps {
  children: ReactNode;
  className?: string;
  /** Delay in seconds before the reveal begins. */
  delay?: number;
  /** Vertical travel distance in px. */
  y?: number;
  /** Animate every time it enters the viewport, not just once. */
  repeat?: boolean;
  as?: "div" | "section" | "li" | "article" | "header";
}

/**
 * Calm entrance animation used across the app. Fully disabled when the user
 * prefers reduced motion — content renders immediately with no transform.
 */
export function Reveal({
  children,
  className,
  delay = 0,
  y = 14,
  repeat = false,
  as = "div",
}: RevealProps) {
  const reduced = usePrefersReducedMotion();
  const MotionTag = motion[as];

  if (reduced) {
    const Tag = as;
    return <Tag className={className}>{children}</Tag>;
  }

  const variants: Variants = {
    hidden: { opacity: 0, y },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1], delay },
    },
  };

  return (
    <MotionTag
      className={cn(className)}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: !repeat, margin: "-60px" }}
      variants={variants}
    >
      {children}
    </MotionTag>
  );
}
