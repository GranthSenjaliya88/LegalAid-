import type { HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-tiny font-medium leading-none tracking-tight [&_svg]:size-3 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        neutral: "border-hairline bg-teal/[0.05] text-muted",
        teal: "border-teal/20 bg-teal/10 text-teal",
        verified: "border-gold/40 bg-gold/[0.12] text-gold-deep",
        success: "border-success/30 bg-success/10 text-success",
        warning: "border-warning/35 bg-warning/[0.12] text-[#8a6416]",
        danger: "border-danger/30 bg-danger/10 text-danger",
        outline: "border-hairline bg-transparent text-muted",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { badgeVariants };
