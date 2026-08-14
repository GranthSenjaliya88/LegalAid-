import { Scale, ShieldCheck, HeartHandshake, Languages } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { Card, CardContent } from "@/components/ui/card";
import { useAppStore } from "@/store/appStore";

const ICONS: LucideIcon[] = [ShieldCheck, Scale, HeartHandshake, Languages];

const PAGE_COPY = {
  en: {
    eyebrow: "About",
    title: "Understanding your rights shouldn't require a lawyer to begin",
    description:
      "LegalAId is a calm legal guide for first-generation litigants in India—a first step toward understanding what happened, what the law may say, and what you can do next.",
    principles: [
      { title: "Source-grounded, always", body: "Every legal reference is retrieved and verified against a corpus of real Indian legal sources before it reaches you." },
      { title: "Honest about uncertainty", body: "When the facts aren't enough to be sure, LegalAId says so plainly instead of guessing or overstating." },
      { title: "Built for first-time litigants", body: "Designed for people facing the legal system for the first time—no jargon, no assumptions, no intimidation." },
      { title: "In your language", body: "Explain your situation in English, Hindi, or Hinglish, and read your rights in language you actually use." },
    ],
    noticeTitle: "Information, not a verdict",
    noticeBody:
      "LegalAId provides general legal information grounded in verified sources. It does not replace a licensed advocate, and it does not decide your case. For decisions about your specific situation, please consult a qualified legal professional.",
  },
  hi: {
    eyebrow: "परिचय",
    title: "अपने अधिकार समझने की शुरुआत के लिए वकील होना ज़रूरी नहीं",
    description:
      "LegalAId भारत में पहली बार कानूनी प्रक्रिया से जुड़ने वाले लोगों के लिए एक शांत कानूनी मार्गदर्शक है—यह समझने का पहला कदम कि क्या हुआ, कानून क्या कह सकता है और आप आगे क्या कर सकते हैं।",
    principles: [
      { title: "हमेशा सत्यापित स्रोतों पर आधारित", body: "हर कानूनी संदर्भ आपको दिखाने से पहले वास्तविक भारतीय कानूनी स्रोतों के संग्रह से खोजा और सत्यापित किया जाता है।" },
      { title: "अनिश्चितता के बारे में ईमानदार", body: "जब तथ्य किसी निश्चित निष्कर्ष के लिए पर्याप्त नहीं होते, तो LegalAId अनुमान लगाने के बजाय इसे साफ़-साफ़ बताता है।" },
      { title: "पहली बार कानूनी प्रक्रिया से जुड़ने वालों के लिए", body: "उन लोगों के लिए बनाया गया है जो पहली बार कानूनी व्यवस्था का सामना कर रहे हैं—बिना कठिन शब्दों, धारणाओं या डर के।" },
      { title: "आपकी भाषा में", body: "अपनी स्थिति अंग्रेज़ी, हिंदी या हिंग्लिश में बताएँ और अपने अधिकार उस भाषा में पढ़ें जिसका आप वास्तव में उपयोग करते हैं।" },
    ],
    noticeTitle: "जानकारी, कोई फैसला नहीं",
    noticeBody:
      "LegalAId सत्यापित स्रोतों पर आधारित सामान्य कानूनी जानकारी देता है। यह किसी लाइसेंस प्राप्त अधिवक्ता की जगह नहीं लेता और आपके मामले का फैसला नहीं करता। अपनी विशेष स्थिति से जुड़े निर्णयों के लिए किसी योग्य कानूनी पेशेवर से सलाह लें।",
  },
} as const;

export function AboutPage() {
  const language = useAppStore((s) => s.language);
  const copy = PAGE_COPY[language];

  return (
    <div className="space-y-10">
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />

      <div className="grid gap-4 sm:grid-cols-2">
        {copy.principles.map((principle, i) => {
          const Icon = ICONS[i];
          return (
            <Reveal key={principle.title} delay={i * 0.05}>
              <Card className="h-full">
                <CardContent className="flex gap-4 pt-6">
                  <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
                    <Icon className="size-5" />
                  </span>
                  <div>
                    <h2 className="text-body font-semibold text-ink">{principle.title}</h2>
                    <p className="mt-1 text-small leading-relaxed text-muted">{principle.body}</p>
                  </div>
                </CardContent>
              </Card>
            </Reveal>
          );
        })}
      </div>

      <Reveal className="rounded-xl border border-teal/20 bg-teal/[0.04] p-6">
        <h2 className="font-display text-h3 text-teal">{copy.noticeTitle}</h2>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">{copy.noticeBody}</p>
      </Reveal>
    </div>
  );
}
