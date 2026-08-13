import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

/**
 * Standard editorial page header: small uppercase eyebrow, serif title,
 * optional supporting line and right-aligned actions.
 */
export function PageHeader({ eyebrow, title, description, actions, className }: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between",
        className,
      )}
    >
      <div className="max-w-prose space-y-2">
        {eyebrow && (
          <p className="text-eyebrow font-semibold uppercase text-gold-deep">{eyebrow}</p>
        )}
        <h1 className="font-display text-h1 leading-[1.05] text-teal">{title}</h1>
        {description && <p className="text-body-lg text-muted">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-3">{actions}</div>}
    </div>
  );
}
