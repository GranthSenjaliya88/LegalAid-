import { Scale, ShieldCheck, HeartHandshake, Languages } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";
import { Card, CardContent } from "@/components/ui/card";

const PRINCIPLES: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: ShieldCheck,
    title: "Source-grounded, always",
    body: "Every legal reference is retrieved and verified against a corpus of real Indian legal sources before it reaches you.",
  },
  {
    icon: Scale,
    title: "Honest about uncertainty",
    body: "When the facts aren't enough to be sure, LegalAId says so plainly instead of guessing or overstating.",
  },
  {
    icon: HeartHandshake,
    title: "Built for first-time litigants",
    body: "Designed for people facing the legal system for the first time — no jargon, no assumptions, no intimidation.",
  },
  {
    icon: Languages,
    title: "In your language",
    body: "Explain your situation in English, Hindi, or Hinglish, and read your rights in language you actually use.",
  },
];

/**
 * About (Part 21). States the mission, who the tool serves, and the principles
 * behind it — including that the AI never decides what the law is.
 */
export function AboutPage() {
  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="About"
        title="Understanding your rights shouldn't require a lawyer to begin"
        description="LegalAId is a calm legal guide for first-generation litigants in India — a first step toward understanding what happened, what the law may say, and what you can do next."
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {PRINCIPLES.map((p, i) => (
          <Reveal key={p.title} delay={i * 0.05}>
            <Card className="h-full">
              <CardContent className="flex gap-4 pt-6">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
                  <p.icon className="size-5" />
                </span>
                <div>
                  <h2 className="text-body font-semibold text-ink">{p.title}</h2>
                  <p className="mt-1 text-small leading-relaxed text-muted">{p.body}</p>
                </div>
              </CardContent>
            </Card>
          </Reveal>
        ))}
      </div>

      <Reveal className="rounded-xl border border-teal/20 bg-teal/[0.04] p-6">
        <h2 className="font-display text-h3 text-teal">Information, not a verdict</h2>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">
          LegalAId provides general legal information grounded in verified sources. It does not
          replace a licensed advocate, and it does not decide your case. For decisions about your
          specific situation, please consult a qualified legal professional.
        </p>
      </Reveal>

      <DisclaimerBanner />
    </div>
  );
}
