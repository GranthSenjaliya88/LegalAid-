import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { FolderClosed, Trash2 } from "lucide-react";
import { casesService } from "@/services/cases";
import { useLibraryStore, type CaseSummary } from "@/store/libraryStore";
import { DOMAINS } from "@/lib/constants";
import { relativeDay, titleCase } from "@/lib/format";
import { useAppStore } from "@/store/appStore";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PIPELINE_STEPS } from "@/lib/constants";

const TOTAL_STEPS = PIPELINE_STEPS.length;

/**
 * My Cases (Part 19). Lists the cases created in this browser (tracked locally,
 * since the backend has no per-user list endpoint) and lets the user re-open or
 * securely delete them.
 */
export function CasesPage() {
  const cases = useLibraryStore((s) => s.cases);
  const removeCase = useLibraryStore((s) => s.removeCase);
  const lang = useAppStore((s) => s.language);
  const [toDelete, setToDelete] = useState<CaseSummary | null>(null);

  const del = useMutation({
    mutationFn: (caseId: string) => casesService.remove(caseId),
    onSuccess: (_res, caseId) => {
      removeCase(caseId);
      toast.success("Case deleted");
      setToDelete(null);
    },
    onError: () => toast.error("Couldn't delete the case. Please try again."),
  });

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="My Cases" title="Cases you've started" description="Re-open a case to continue, or remove it from this device." />

      {cases.length === 0 ? (
        <EmptyState
          icon={FolderClosed}
          title="No cases yet"
          description="When you describe a legal problem, it will appear here so you can return to it anytime."
          action={
            <Button asChild>
              <Link to="/">Start a legal question</Link>
            </Button>
          }
        />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {cases.map((c) => {
            const domainMeta = c.domain ? DOMAINS[c.domain] : null;
            return (
              <li
                key={c.caseId}
                className="flex flex-col rounded-xl border border-hairline bg-surface p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="line-clamp-2 text-body font-semibold text-ink">{c.title}</h2>
                    <p className="mt-1 text-tiny text-muted">Created {relativeDay(c.createdAt)}</p>
                  </div>
                  {domainMeta && (
                    <Badge variant="neutral" className="shrink-0">
                      <domainMeta.icon className="size-3" />
                      {lang === "hi" ? domainMeta.labelHi : domainMeta.label}
                    </Badge>
                  )}
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{titleCase(c.status)}</Badge>
                  <span className="text-tiny text-muted">
                    {Math.min(c.stepsCompleted, TOTAL_STEPS)}/{TOTAL_STEPS} steps
                  </span>
                </div>

                <div className="mt-4 flex items-center gap-2 pt-1">
                  <Button asChild size="sm" className="flex-1">
                    <Link to={`/case/${c.caseId}`}>Open case</Link>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setToDelete(c)}
                    aria-label={`Delete ${c.title}`}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <Dialog open={Boolean(toDelete)} onOpenChange={(open) => !open && setToDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete this case?</DialogTitle>
            <DialogDescription>
              This permanently removes “{toDelete?.title}” and any documents created from it. This
              can't be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setToDelete(null)} disabled={del.isPending}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => toDelete && del.mutate(toDelete.caseId)}
              disabled={del.isPending}
            >
              {del.isPending ? "Deleting…" : "Delete case"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
