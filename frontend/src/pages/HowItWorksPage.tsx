import { ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";

/** Process steps — UI copy describing how the assistant works (not legal content). */
const STEPS: { title: string; body: string }[] = [
  {
    title: "You tell us what happened",
    body: "Describe your situation in your own words — English, Hindi, or Hinglish. No legal terms needed.",
  },
  {
    title: "We extract the facts",
    body: "The assistant pulls out the key details — what happened, where, how much, and when — and shows them back to you to correct.",
  },
  {
    title: "We ask only what's missing",
    body: "If something important is unclear, you'll get a short, plain-language question instead of a legal form.",
  },
  {
    title: "We find verified law",
    body: "Relevant provisions are retrieved from a verified corpus of Indian legal sources before anything is explained.",
  },
  {
    title: "We check whether it applies",
    body: "Each provision is weighed against your specific facts and jurisdiction — not applied blindly.",
  },
  {
    title: "We explain your rights",
    body: "You get a calm, plain-language summary of what the law may mean for you, with the reasoning shown openly.",
  },
  {
    title: "We show useful evidence and next steps",
    body: "A checklist of documents that may strengthen your case, and a clear roadmap of what you can do next.",
  },
  {
    title: "We prepare your draft",
    body: "When you're ready, generate an editable draft document grounded in your verified case details.",
  },
];

/**
 * How It Works (Parts 21 & 27). Explains the source-grounded pipeline in plain
 * language and states clearly that the AI does not decide what the law is.
 */
export function HowItWorksPage() {
  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="How It Works"
        title="A calm, source-grounded path from confusion to clarity"
        description="LegalAId walks with you through eight steps — grounding every explanation in verified legal sources rather than guessing."
      />

      <ol className="relative space-y-0">
        {STEPS.map((step, i) => {
          const last = i === STEPS.length - 1;
          return (
            <Reveal as="li" key={step.title} delay={i * 0.04} className="flex gap-4">
              <div className="flex flex-col items-center">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-teal text-small font-semibold text-ivory-soft">
                  {i + 1}
                </span>
                {!last && <span className="my-1 w-px flex-1 bg-hairline" aria-hidden="true" />}
              </div>
              <div className={last ? "pb-0" : "pb-7"}>
                <h2 className="text-body font-semibold text-ink">{step.title}</h2>
                <p className="mt-1 max-w-2xl text-small leading-relaxed text-muted">{step.body}</p>
              </div>
            </Reveal>
          );
        })}
      </ol>

      <Reveal className="rounded-xl border border-teal/20 bg-teal/[0.04] p-6">
        <p className="flex items-center gap-2 font-display text-h4 text-teal">
          <ShieldCheck className="size-5 text-gold-deep" />
          AI does not decide what the law is
        </p>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">
          LegalAId uses a verified legal knowledge system to retrieve and check real legal sources
          before anything is presented to you. The AI's role is to explain — clearly and honestly —
          never to invent provisions or fill gaps with guesses. When information is insufficient, it
          says so.
        </p>
      </Reveal>

      <DisclaimerBanner />
    </div>
  );
}
