import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { FolderClosed, Trash2 } from "lucide-react";
import { casesService } from "@/services/cases";
import { useLibraryStore, type CaseSummary } from "@/store/libraryStore";
import { DOMAINS, PIPELINE_STEPS } from "@/lib/constants";
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

const TOTAL_STEPS = PIPELINE_STEPS.length;

const HINDI_STATUS: Record<string, string> = {
  new: "नया",
  received: "प्राप्त",
  classified: "वर्गीकृत",
  retrieved: "जानकारी मिली",
  clarified: "स्पष्ट किया गया",
  explained: "समझाया गया",
  documented: "दस्तावेज बनाया गया",
  complete: "पूर्ण",
};

/** Cases created in this browser, with reopen and delete actions. */
export function CasesPage() {
  const cases = useLibraryStore((s) => s.cases);
  const removeCase = useLibraryStore((s) => s.removeCase);
  const lang = useAppStore((s) => s.language);
  const hi = lang === "hi";
  const [toDelete, setToDelete] = useState<CaseSummary | null>(null);

  const del = useMutation({
    mutationFn: (caseId: string) => casesService.remove(caseId),
    onSuccess: (_res, caseId) => {
      removeCase(caseId);
      toast.success(hi ? "मामला हटा दिया गया" : "Case deleted");
      setToDelete(null);
    },
    onError: () =>
      toast.error(
        hi
          ? "मामला हटाया नहीं जा सका। कृपया फिर कोशिश करें।"
          : "Couldn't delete the case. Please try again.",
      ),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={hi ? "मेरे मामले" : "My Cases"}
        title={hi ? "आपके शुरू किए गए मामले" : "Cases you've started"}
        description={
          hi
            ? "जारी रखने के लिए मामला दोबारा खोलें या इसे इस डिवाइस से हटाएँ।"
            : "Re-open a case to continue, or remove it from this device."
        }
      />

      {cases.length === 0 ? (
        <EmptyState
          icon={FolderClosed}
          title={hi ? "अभी कोई मामला नहीं" : "No cases yet"}
          description={
            hi
              ? "जब आप कोई कानूनी समस्या बताएँगे, तो वह यहाँ दिखाई देगी ताकि आप कभी भी उस पर लौट सकें।"
              : "When you describe a legal problem, it will appear here so you can return to it anytime."
          }
          action={
            <Button asChild variant="gold">
              <Link to="/">{hi ? "कानूनी प्रश्न पूछें" : "Start a legal question"}</Link>
            </Button>
          }
        />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {cases.map((c) => {
            const domainMeta = c.domain ? DOMAINS[c.domain] : null;
            const status = hi ? (HINDI_STATUS[c.status] ?? titleCase(c.status)) : titleCase(c.status);
            return (
              <li
                key={c.caseId}
                className="flex flex-col rounded-xl border border-hairline bg-surface p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="line-clamp-2 text-body font-semibold text-ink">{c.title}</h2>
                    <p className="mt-1 text-tiny text-muted">
                      {hi ? "बनाया गया" : "Created"} {relativeDay(c.createdAt, lang)}
                    </p>
                  </div>
                  {domainMeta && (
                    <Badge variant="neutral" className="shrink-0">
                      <domainMeta.icon className="size-3" />
                      {hi ? domainMeta.labelHi : domainMeta.label}
                    </Badge>
                  )}
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{status}</Badge>
                  <span className="text-tiny text-muted">
                    {Math.min(c.stepsCompleted, TOTAL_STEPS)}/{TOTAL_STEPS} {hi ? "चरण" : "steps"}
                  </span>
                </div>

                <div className="mt-4 flex items-center gap-2 pt-1">
                  <Button asChild size="sm" className="flex-1">
                    <Link to={`/case/${c.caseId}`}>{hi ? "मामला खोलें" : "Open case"}</Link>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setToDelete(c)}
                    aria-label={hi ? `${c.title} हटाएँ` : `Delete ${c.title}`}
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
            <DialogTitle>{hi ? "यह मामला हटाएँ?" : "Delete this case?"}</DialogTitle>
            <DialogDescription>
              {hi
                ? `इससे “${toDelete?.title}” और उससे बने सभी दस्तावेज हमेशा के लिए हट जाएँगे। इसे वापस नहीं किया जा सकता।`
                : `This permanently removes “${toDelete?.title}” and any documents created from it. This can't be undone.`}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setToDelete(null)} disabled={del.isPending}>
              {hi ? "रद्द करें" : "Cancel"}
            </Button>
            <Button
              variant="danger"
              onClick={() => toDelete && del.mutate(toDelete.caseId)}
              disabled={del.isPending}
            >
              {del.isPending ? (hi ? "हटाया जा रहा है…" : "Deleting…") : hi ? "मामला हटाएँ" : "Delete case"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
