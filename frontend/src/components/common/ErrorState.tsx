import { type ReactNode } from "react";
import { AlertTriangle, RefreshCw, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  description?: ReactNode;
  onRetry?: () => void;
  retryLabel?: string;
  /** Use the offline variant when the service is unreachable. */
  variant?: "error" | "offline";
  className?: string;
}

/**
 * Friendly, non-alarming error surface with an optional retry. Copy avoids
 * technical jargon so first-time users aren't intimidated.
 */
export function ErrorState({
  title,
  description,
  onRetry,
  retryLabel = "Try again",
  variant = "error",
  className,
}: ErrorStateProps) {
  const Icon = variant === "offline" ? WifiOff : AlertTriangle;
  const resolvedTitle =
    title ?? (variant === "offline" ? "Can't reach the assistant" : "Something went wrong");
  const resolvedDescription =
    description ??
    (variant === "offline"
      ? "The LegalAId service isn't responding right now. Please check your connection and try again."
      : "We hit a snag processing this. You can try again in a moment.");

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4 rounded-xl border border-danger/25 bg-danger/[0.04] px-6 py-12 text-center",
        className,
      )}
      role="alert"
    >
      <span className="flex size-12 items-center justify-center rounded-full bg-danger/10 text-danger">
        <Icon className="size-6" strokeWidth={1.7} />
      </span>
      <div className="max-w-sm space-y-1.5">
        <p className="text-h4 font-semibold text-ink">{resolvedTitle}</p>
        <p className="text-small leading-relaxed text-muted">{resolvedDescription}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="size-4" />
          {retryLabel}
        </Button>
      )}
    </div>
  );
}
