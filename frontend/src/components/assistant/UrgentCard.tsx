import { AlertTriangle, ShieldAlert } from "lucide-react";
import type { EmergencyPlan } from "@/types";
import { useAppStore } from "@/store/appStore";

/**
 * Urgent action card (Part 7). Shown when the backend flags a situation as
 * time-sensitive. Tone stays steady and directive — clear steps, not alarm.
 */
export function UrgentCard({ plan }: { plan: EmergencyPlan }) {
  const hi = useAppStore((s) => s.language) === "hi";
  const steps = plan.immediate_steps?.length ? plan.immediate_steps : plan.steps ?? [];
  const hasContent =
    plan.is_urgent || plan.message || plan.warning || steps.length > 0 || (plan.preserve_evidence?.length ?? 0) > 0;
  if (!hasContent) return null;

  return (
    <section
      className="overflow-hidden rounded-xl border border-danger/30 bg-danger/[0.04]"
      aria-labelledby="urgent-title"
    >
      <div className="flex items-center gap-2 border-b border-danger/20 bg-danger/[0.06] px-5 py-3">
        <ShieldAlert className="size-5 text-danger" />
        <h2 id="urgent-title" className="text-h4 font-semibold text-danger">
          {plan.title || (hi ? "समय महत्वपूर्ण है—जल्द कार्रवाई करें" : "Time-sensitive—act soon")}
        </h2>
      </div>
      <div className="space-y-4 p-5">
        {(plan.message || plan.warning) && (
          <p className="text-small leading-relaxed text-ink">{plan.message || plan.warning}</p>
        )}

        {steps.length > 0 && (
          <div>
            <p className="text-tiny font-semibold uppercase tracking-wide text-danger">
              {hi ? "अभी यह करें" : "Do this now"}
            </p>
            <ol className="mt-2 space-y-2">
              {steps.map((s, i) => (
                <li key={i} className="flex gap-2.5 text-small text-ink">
                  <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-danger/15 text-tiny font-semibold text-danger">
                    {i + 1}
                  </span>
                  <span className="leading-relaxed">{s}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {plan.preserve_evidence && plan.preserve_evidence.length > 0 && (
          <div>
            <p className="text-tiny font-semibold uppercase tracking-wide text-muted">
              {hi ? "सबूत के रूप में सुरक्षित रखें" : "Preserve as evidence"}
            </p>
            <ul className="mt-2 space-y-1">
              {plan.preserve_evidence.map((e, i) => (
                <li key={i} className="flex items-start gap-2 text-small text-ink">
                  <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-warning" />
                  <span className="leading-relaxed">{e}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {plan.reporting_path && (
          <div className="rounded-lg border border-hairline bg-surface px-4 py-3">
            <p className="text-tiny font-semibold uppercase tracking-wide text-muted">
              {hi ? "कहाँ रिपोर्ट करें" : "Where to report"}
            </p>
            <p className="mt-1 text-small leading-relaxed text-ink">{plan.reporting_path}</p>
          </div>
        )}
      </div>
    </section>
  );
}
