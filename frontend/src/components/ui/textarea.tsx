import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "flex min-h-[7rem] w-full rounded-lg border border-hairline bg-surface px-3.5 py-3 text-body leading-relaxed text-ink shadow-sm transition-colors",
      "placeholder:text-muted/70",
      "focus-visible:border-teal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/60",
      "disabled:cursor-not-allowed disabled:opacity-55",
      "resize-y",
      className,
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";
