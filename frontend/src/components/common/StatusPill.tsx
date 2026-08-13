import { useHealth } from "@/hooks/useHealth";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

/**
 * Live service status indicator (Part 5). Polls the backend health endpoint
 * and reflects reachability with a calm dot — never alarming.
 */
export function StatusPill({ className }: { className?: string }) {
  const { t } = useT();
  const { data, isLoading, isError } = useHealth();

  const online = !isError && data?.status === "ok";
  const state = isLoading ? "checking" : online ? "ready" : "offline";

  const label =
    state === "ready"
      ? t("status.ready")
      : state === "checking"
        ? t("status.checking")
        : t("status.offline");

  const dotClass =
    state === "ready"
      ? "bg-success"
      : state === "checking"
        ? "bg-warning"
        : "bg-danger";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-hairline bg-surface px-3 py-1 text-tiny font-medium text-muted",
        className,
      )}
      role="status"
      aria-live="polite"
    >
      <span className="relative flex size-2">
        {state === "ready" && (
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-success/60" />
        )}
        <span className={cn("relative inline-flex size-2 rounded-full", dotClass)} />
      </span>
      {label}
    </span>
  );
}
