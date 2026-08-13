import { type ComponentType, type ReactNode } from "react";
import { type LucideProps } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon?: ComponentType<LucideProps>;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
}

/**
 * Neutral, reassuring empty state. Used whenever a list or result set is
 * legitimately empty (no cases yet, no search matches, etc.).
 */
export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-hairline bg-surface/60 px-6 py-14 text-center",
        className,
      )}
    >
      {Icon && (
        <span className="flex size-12 items-center justify-center rounded-full bg-teal/[0.06] text-teal">
          <Icon className="size-6" strokeWidth={1.6} />
        </span>
      )}
      <div className="max-w-sm space-y-1.5">
        <p className="text-h4 font-semibold text-ink">{title}</p>
        {description && <p className="text-small leading-relaxed text-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}
