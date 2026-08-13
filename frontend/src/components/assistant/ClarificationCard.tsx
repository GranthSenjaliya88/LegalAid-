import { useState } from "react";
import { HelpCircle } from "lucide-react";
import type { AnswerValue, CaseFacts } from "@/types";
import { INDIAN_STATES } from "@/lib/constants";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const L = {
  en: {
    title: "A few quick questions",
    hint: "Answering these helps us find the most relevant law. You can skip if you're unsure.",
    submit: "Continue",
    skip: "Skip for now",
    selectState: "Select a state",
  },
  hi: {
    title: "कुछ छोटे सवाल",
    hint: "इनका उत्तर देने से हमें सबसे प्रासंगिक कानून खोजने में मदद मिलती है। अनिश्चित हों तो छोड़ सकते हैं।",
    submit: "आगे बढ़ें",
    skip: "अभी छोड़ें",
    selectState: "राज्य चुनें",
  },
} as const;

/** Infer which CaseFacts field a free-text question is asking about. */
function inferKey(question: string): keyof CaseFacts | null {
  const q = question.toLowerCase();
  if (q.includes("state") || q.includes("union territory")) return "state";
  if (q.includes("amount") || q.includes("₹") || q.includes("rupee") || q.includes("money") || q.includes("paid")) return "amount";
  if (q.includes("when") || q.includes("date")) return "date";
  if (q.includes("where") || q.includes("location") || q.includes("address")) return "location";
  if (q.includes("agreement") || q.includes("contract") || q.includes("in writing") || q.includes("written")) return "agreement_exists";
  if (q.includes("notice") || q.includes("complaint") || q.includes("reported") || q.includes("informed")) return "notice_given";
  if (q.includes("who") || q.includes("parties") || q.includes("landlord") || q.includes("employer") || q.includes("seller")) return "parties";
  if (q.includes("want") || q.includes("outcome") || q.includes("seeking") || q.includes("resolution") || q.includes("hoping")) return "desired_outcome";
  return null;
}

function parseYesNo(text: string): boolean | null {
  const t = text.trim().toLowerCase();
  if (/^(yes|y|haan|haa|हाँ|हां|yeah|yep|true)\b/.test(t)) return true;
  if (/^(no|n|nahi|nahin|नहीं|nope|false)\b/.test(t)) return false;
  return null;
}

interface ClarificationCardProps {
  questions: string[];
  facts?: CaseFacts;
  onSubmit: (answers: Record<string, AnswerValue>) => void;
  onSkip: () => void;
  pending?: boolean;
}

/**
 * Clarification step (Part 10). Renders up to three questions; answers are
 * mapped onto real fact fields where possible, and anything unmapped is
 * preserved in additional_facts so no detail is lost.
 */
export function ClarificationCard({ questions, facts, onSubmit, onSkip, pending = false }: ClarificationCardProps) {
  const lang = useAppStore((s) => s.language);
  const t = L[lang];
  const [values, setValues] = useState<string[]>(() => questions.map(() => ""));

  const setAt = (i: number, v: string) =>
    setValues((prev) => prev.map((x, idx) => (idx === i ? v : x)));

  const submit = () => {
    const answers: Record<string, AnswerValue> = {};
    const extra: string[] = [];

    questions.forEach((q, i) => {
      const ans = values[i]?.trim();
      if (!ans) return;
      const key = inferKey(q);
      if (key === "agreement_exists" || key === "notice_given") {
        const parsed = parseYesNo(ans);
        if (parsed !== null) answers[key] = parsed;
        else extra.push(`${q} ${ans}`);
      } else if (key) {
        answers[key] = ans;
      } else {
        extra.push(`${q} ${ans}`);
      }
    });

    if (extra.length) {
      const existing = facts?.additional_facts ? String(facts.additional_facts).trim() : "";
      answers.additional_facts = [existing, ...extra].filter(Boolean).join("\n");
    }

    onSubmit(answers);
  };

  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle className={cn("flex items-center gap-2", lang === "hi" && "font-deva")}>
          <HelpCircle className="size-5 text-gold-deep" />
          {t.title}
        </CardTitle>
        <p className={cn("text-small text-muted", lang === "hi" && "font-deva")}>{t.hint}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {questions.map((q, i) => {
            const key = inferKey(q);
            const id = `clarify-${i}`;
            return (
              <div key={i} className="space-y-1.5">
                <Label htmlFor={id} className={cn("leading-snug", lang === "hi" && "font-deva")}>
                  {q}
                </Label>
                {key === "state" ? (
                  <Select value={values[i] || undefined} onValueChange={(v) => setAt(i, v)}>
                    <SelectTrigger id={id}>
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
                ) : (
                  <Input
                    id={id}
                    value={values[i]}
                    onChange={(e) => setAt(i, e.target.value)}
                    disabled={pending}
                    className={cn(lang === "hi" && "font-deva")}
                  />
                )}
              </div>
            );
          })}

          <div className="flex flex-col-reverse gap-3 pt-1 sm:flex-row sm:items-center sm:justify-end">
            <Button variant="ghost" onClick={onSkip} disabled={pending}>
              <span className={cn(lang === "hi" && "font-deva")}>{t.skip}</span>
            </Button>
            <Button onClick={submit} disabled={pending}>
              <span className={cn(lang === "hi" && "font-deva")}>{t.submit}</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
