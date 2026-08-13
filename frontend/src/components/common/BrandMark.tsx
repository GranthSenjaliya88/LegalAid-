import { Scale } from "lucide-react";
import { cn } from "@/lib/utils";

interface BrandMarkProps {
  /** Show the wordmark text next to the emblem. */
  showWord?: boolean;
  className?: string;
  size?: "sm" | "md";
}

/**
 * LegalAId brand lockup: a scales-of-justice emblem in teal with a small
 * gold accent, paired with the wordmark set in the display serif.
 */
export function BrandMark({ showWord = true, className, size = "md" }: BrandMarkProps) {
  const box = size === "sm" ? "size-8" : "size-9";
  const icon = size === "sm" ? "size-4" : "size-[1.15rem]";

  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span className={cn("relative flex items-center justify-center rounded-lg bg-teal text-ivory-soft", box)}>
        <Scale className={icon} strokeWidth={1.9} />
        <span className="absolute -right-0.5 -top-0.5 size-2 rounded-full bg-gold ring-2 ring-ivory" />
      </span>
      {showWord && (
        <span className="font-display text-h4 leading-none text-teal">
          Legal<span className="text-gold-deep">AId</span>
        </span>
      )}
    </span>
  );
}
