import { useState, type ReactNode } from "react";
import { useForm, Controller, type Control } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Pencil, X } from "lucide-react";
import type { AnswerValue, CaseFacts } from "@/types";
import { INDIAN_STATES } from "@/lib/constants";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const factSchema = z.object({
  incident: z.string().trim().min(5, "Please describe what happened."),
  parties: z.string().trim().optional(),
  amount: z.string().trim().optional(),
  date: z.string().trim().optional(),
  location: z.string().trim().optional(),
  state: z.string().trim().optional(),
  desired_outcome: z.string().trim().optional(),
  agreement_exists: z.enum(["yes", "no", "unknown"]),
  notice_given: z.enum(["yes", "no", "unknown"]),
  additional_facts: z.string().trim().optional(),
});
type FactForm = z.infer<typeof factSchema>;

const L = {
  en: {
    title: "What we understood",
    hint: "We extracted these details from your description. Please check and correct anything that's wrong — accurate facts lead to more relevant law.",
    edit: "Correct details",
    save: "Save & re-analyze",
    cancel: "Cancel",
    incident: "What happened",
    parties: "Who is involved",
    amount: "Amount involved (₹)",
    date: "When it happened",
    location: "Where it happened",
    state: "State / Union Territory",
    desired_outcome: "What you would like to happen",
    agreement_exists: "Was there a written agreement or contract?",
    notice_given: "Have you already sent any notice or complaint?",
    additional_facts: "Anything else we should know",
    yes: "Yes",
    no: "No",
    unknown: "Not sure",
    notProvided: "Not provided",
    selectState: "Select a state",
  },
  hi: {
    title: "हमने यह समझा",
    hint: "ये विवरण हमने आपके विवरण से निकाले हैं। कृपया जाँचें और गलत जानकारी सुधारें — सही तथ्यों से अधिक प्रासंगिक कानून मिलता है।",
    edit: "विवरण सुधारें",
    save: "सहेजें और दोबारा जाँचें",
    cancel: "रद्द करें",
    incident: "क्या हुआ",
    parties: "कौन शामिल है",
    amount: "राशि (₹)",
    date: "कब हुआ",
    location: "कहाँ हुआ",
    state: "राज्य / केंद्र शासित प्रदेश",
    desired_outcome: "आप क्या चाहते हैं",
    agreement_exists: "क्या कोई लिखित अनुबंध या समझौता था?",
    notice_given: "क्या आपने पहले कोई नोटिस या शिकायत भेजी है?",
    additional_facts: "और कुछ जो हमें जानना चाहिए",
    yes: "हाँ",
    no: "नहीं",
    unknown: "पता नहीं",
    notProvided: "नहीं दिया गया",
    selectState: "राज्य चुनें",
  },
} as const;

function boolToChoice(v: boolean | null | undefined): "yes" | "no" | "unknown" {
  if (v === true) return "yes";
  if (v === false) return "no";
  return "unknown";
}
function choiceToAnswer(v: "yes" | "no" | "unknown"): AnswerValue {
  if (v === "yes") return true;
  if (v === "no") return false;
  return null; // "unknown" → don't overwrite existing value on the backend
}

interface FactCardProps {
  facts: CaseFacts;
  onApply: (answers: Record<string, AnswerValue>) => void;
  pending?: boolean;
}

/**
 * Editable summary of AI-extracted facts (Part 9). Corrections are submitted
 * as a *complete* answer set (not just changed fields) to protect against the
 * backend clarify/respond merge dropping unspecified fields.
 */
export function FactCard({ facts, onApply, pending = false }: FactCardProps) {
  const lang = useAppStore((s) => s.language);
  const t = L[lang];
  const [editing, setEditing] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FactForm>({
    resolver: zodResolver(factSchema),
    defaultValues: toForm(facts),
  });

  const startEdit = () => {
    reset(toForm(facts));
    setEditing(true);
  };

  const submit = handleSubmit((values) => {
    const answers: Record<string, AnswerValue> = {
      incident: values.incident.trim(),
      parties: values.parties?.trim() || null,
      amount: values.amount?.trim() || null,
      date: values.date?.trim() || null,
      location: values.location?.trim() || null,
      state: values.state?.trim() || null,
      desired_outcome: values.desired_outcome?.trim() || null,
      agreement_exists: choiceToAnswer(values.agreement_exists),
      notice_given: choiceToAnswer(values.notice_given),
      additional_facts: values.additional_facts?.trim() || null,
    };
    setEditing(false);
    onApply(answers);
  });

  if (!editing) {
    return (
      <Card>
        <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
          <div className="space-y-1">
            <CardTitle className={cn(lang === "hi" && "font-deva")}>{t.title}</CardTitle>
            <p className={cn("text-small text-muted", lang === "hi" && "font-deva")}>{t.hint}</p>
          </div>
          <Button variant="outline" size="sm" onClick={startEdit} disabled={pending}>
            <Pencil className="size-4" />
            <span className={cn(lang === "hi" && "font-deva")}>{t.edit}</span>
          </Button>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-x-8 gap-y-4 sm:grid-cols-2">
            <ReadRow label={t.incident} value={asText(facts.incident)} full lang={lang} />
            <ReadRow label={t.parties} value={asText(facts.parties)} lang={lang} />
            <ReadRow label={t.amount} value={asText(facts.amount)} lang={lang} />
            <ReadRow label={t.date} value={asText(facts.date)} lang={lang} />
            <ReadRow label={t.location} value={asText(facts.location)} lang={lang} />
            <ReadRow label={t.state} value={asText(facts.state)} lang={lang} />
            <ReadRow label={t.desired_outcome} value={asText(facts.desired_outcome)} lang={lang} />
            <ReadRow label={t.agreement_exists} value={boolText(facts.agreement_exists, t)} lang={lang} />
            <ReadRow label={t.notice_given} value={boolText(facts.notice_given, t)} lang={lang} />
            {facts.additional_facts && (
              <ReadRow label={t.additional_facts} value={asText(facts.additional_facts)} full lang={lang} />
            )}
          </dl>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between gap-3 space-y-0">
        <CardTitle className={cn(lang === "hi" && "font-deva")}>{t.edit}</CardTitle>
        <Button variant="ghost" size="icon-sm" onClick={() => setEditing(false)} aria-label={t.cancel}>
          <X className="size-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <form onSubmit={submit} className="space-y-5">
          <Field label={t.incident} htmlFor="incident" error={errors.incident?.message} lang={lang}>
            <Textarea id="incident" {...register("incident")} className={cn(lang === "hi" && "font-deva")} />
          </Field>

          <div className="grid gap-5 sm:grid-cols-2">
            <Field label={t.parties} htmlFor="parties" lang={lang}>
              <Input id="parties" {...register("parties")} />
            </Field>
            <Field label={t.amount} htmlFor="amount" lang={lang}>
              <Input id="amount" inputMode="numeric" {...register("amount")} />
            </Field>
            <Field label={t.date} htmlFor="date" lang={lang}>
              <Input id="date" {...register("date")} />
            </Field>
            <Field label={t.location} htmlFor="location" lang={lang}>
              <Input id="location" {...register("location")} />
            </Field>
          </div>

          <Field label={t.state} htmlFor="state" lang={lang}>
            <Controller
              control={control}
              name="state"
              render={({ field }) => (
                <Select value={field.value || undefined} onValueChange={field.onChange}>
                  <SelectTrigger id="state">
                    <SelectValue placeholder={t.selectState} />
                  </SelectTrigger>
                  <SelectContent>
                    {INDIAN_STATES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </Field>

          <Field label={t.desired_outcome} htmlFor="desired_outcome" lang={lang}>
            <Input id="desired_outcome" {...register("desired_outcome")} className={cn(lang === "hi" && "font-deva")} />
          </Field>

          <div className="grid gap-5 sm:grid-cols-2">
            <ChoiceField label={t.agreement_exists} name="agreement_exists" control={control} t={t} lang={lang} />
            <ChoiceField label={t.notice_given} name="notice_given" control={control} t={t} lang={lang} />
          </div>

          <Field label={t.additional_facts} htmlFor="additional_facts" lang={lang}>
            <Textarea
              id="additional_facts"
              {...register("additional_facts")}
              className={cn("min-h-[5rem]", lang === "hi" && "font-deva")}
            />
          </Field>

          <div className="flex items-center justify-end gap-3">
            <Button type="button" variant="ghost" onClick={() => setEditing(false)} disabled={pending}>
              <span className={cn(lang === "hi" && "font-deva")}>{t.cancel}</span>
            </Button>
            <Button type="submit" disabled={pending}>
              <span className={cn(lang === "hi" && "font-deva")}>{t.save}</span>
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

/* ---- helpers ---- */

function toForm(facts: CaseFacts): FactForm {
  return {
    incident: asText(facts.incident) ?? "",
    parties: asText(facts.parties) ?? "",
    amount: facts.amount != null ? String(facts.amount) : "",
    date: asText(facts.date) ?? "",
    location: asText(facts.location) ?? "",
    state: asText(facts.state) ?? "",
    desired_outcome: asText(facts.desired_outcome) ?? "",
    agreement_exists: boolToChoice(facts.agreement_exists),
    notice_given: boolToChoice(facts.notice_given),
    additional_facts: asText(facts.additional_facts) ?? "",
  };
}

function asText(v: unknown): string | undefined {
  if (v == null) return undefined;
  const s = String(v).trim();
  return s.length ? s : undefined;
}

function boolText(v: boolean | null | undefined, t: (typeof L)["en"] | (typeof L)["hi"]): string | undefined {
  if (v === true) return t.yes;
  if (v === false) return t.no;
  return undefined;
}

function ReadRow({
  label,
  value,
  full,
  lang,
}: {
  label: string;
  value?: string;
  full?: boolean;
  lang: "en" | "hi";
}) {
  return (
    <div className={cn(full && "sm:col-span-2")}>
      <dt className={cn("text-tiny font-medium uppercase tracking-wide text-muted", lang === "hi" && "font-deva")}>
        {label}
      </dt>
      <dd className={cn("mt-1 text-body text-ink", lang === "hi" && "font-deva", !value && "italic text-muted/70")}>
        {value ?? (lang === "hi" ? "नहीं दिया गया" : "Not provided")}
      </dd>
    </div>
  );
}

function Field({
  label,
  htmlFor,
  error,
  children,
  lang,
}: {
  label: string;
  htmlFor: string;
  error?: string;
  children: ReactNode;
  lang: "en" | "hi";
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={htmlFor} className={cn(lang === "hi" && "font-deva")}>
        {label}
      </Label>
      {children}
      {error && (
        <p className="text-tiny text-danger" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function ChoiceField({
  label,
  name,
  control,
  t,
  lang,
}: {
  label: string;
  name: "agreement_exists" | "notice_given";
  control: Control<FactForm>;
  t: (typeof L)["en"] | (typeof L)["hi"];
  lang: "en" | "hi";
}) {
  return (
    <div className="space-y-2">
      <Label className={cn(lang === "hi" && "font-deva")}>{label}</Label>
      <Controller
        control={control}
        name={name}
        render={({ field }) => (
          <RadioGroup value={field.value} onValueChange={field.onChange} className="flex flex-wrap gap-4">
            {(["yes", "no", "unknown"] as const).map((opt) => (
              <label key={opt} className="flex cursor-pointer items-center gap-2 text-small text-ink">
                <RadioGroupItem value={opt} />
                <span className={cn(lang === "hi" && "font-deva")}>{t[opt]}</span>
              </label>
            ))}
          </RadioGroup>
        )}
      />
    </div>
  );
}
