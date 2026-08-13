import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      ref={ref}
      type={type}
      className={cn(
        "flex h-11 w-full rounded-lg border border-hairline bg-surface px-3.5 py-2 text-body text-ink shadow-sm transition-colors",
        "placeholder:text-muted/70",
        "focus-visible:border-teal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/60",
        "disabled:cursor-not-allowed disabled:opacity-55",
        "file:border-0 file:bg-transparent file:text-small file:font-medium",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";
