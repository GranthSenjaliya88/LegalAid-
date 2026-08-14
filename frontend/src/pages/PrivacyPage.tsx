import { Lock, Trash2, EyeOff, ShieldCheck, ScrollText } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { useAppStore } from "@/store/appStore";

const SECTION_ICONS: LucideIcon[] = [Lock, EyeOff, ScrollText, Trash2];

const PAGE_COPY = {
  en: {
    eyebrow: "Privacy & Safety",
    title: "Your privacy comes first",
    description:
      "LegalAId is built to help you understand your rights without putting your personal security at risk.",
    reminderTitle: "A quick safety reminder",
    reminder: "Never enter passwords, OTPs, PINs, or unnecessary sensitive information.",
    sections: [
      {
        title: "Never enter sensitive credentials",
        body: "Never enter passwords, OTPs, PINs, or unnecessary sensitive information. LegalAId never needs them to explain your rights, and they are never required to use any feature.",
      },
      {
        title: "We minimize what we handle",
        body: "Only the details needed to understand your situation are processed. Sensitive credentials are never logged, and internal traces are redacted.",
      },
      {
        title: "What stays on this device",
        body: "A lightweight list of the cases and drafts you've created is kept in your browser so you can find them again. No legal content is stored there.",
      },
      {
        title: "Deleting a case removes it",
        body: "When you delete a case, its record and associated documents are removed from the backend, and it disappears from this device too.",
      },
    ],
    noticeTitle: "Information, not legal advice",
    noticeBody:
      "LegalAId provides general legal information grounded in verified sources—not legal advice. For decisions about your specific situation, consult a licensed advocate.",
  },
  hi: {
    eyebrow: "गोपनीयता और सुरक्षा",
    title: "आपकी गोपनीयता सबसे पहले",
    description:
      "LegalAId आपको अपनी व्यक्तिगत सुरक्षा को जोखिम में डाले बिना अपने अधिकार समझने में मदद करने के लिए बनाया गया है।",
    reminderTitle: "एक जरूरी सुरक्षा याद दिलाना",
    reminder: "पासवर्ड, OTP, PIN या अनावश्यक संवेदनशील जानकारी कभी दर्ज न करें।",
    sections: [
      {
        title: "संवेदनशील जानकारी कभी दर्ज न करें",
        body: "पासवर्ड, OTP, PIN या अनावश्यक संवेदनशील जानकारी कभी दर्ज न करें। आपके अधिकार समझाने के लिए LegalAId को इनकी जरूरत नहीं होती और किसी सुविधा के उपयोग के लिए भी ये आवश्यक नहीं हैं।",
      },
      {
        title: "हम केवल जरूरी जानकारी लेते हैं",
        body: "आपकी स्थिति समझने के लिए केवल आवश्यक विवरण ही संसाधित किए जाते हैं। संवेदनशील जानकारी कभी लॉग नहीं की जाती और आंतरिक रिकॉर्ड से निजी विवरण हटा दिए जाते हैं।",
      },
      {
        title: "इस डिवाइस पर क्या रहता है",
        body: "आपके बनाए मामलों और ड्राफ्ट की एक छोटी सूची ब्राउज़र में रहती है, ताकि आप उन्हें दोबारा खोज सकें। उसमें कोई कानूनी सामग्री संग्रहीत नहीं होती।",
      },
      {
        title: "मामला हटाने पर वह मिट जाता है",
        body: "मामला हटाने पर उसका रिकॉर्ड और उससे जुड़े दस्तावेज सर्वर से हटा दिए जाते हैं और वह इस डिवाइस से भी गायब हो जाता है।",
      },
    ],
    noticeTitle: "जानकारी, कानूनी सलाह नहीं",
    noticeBody:
      "LegalAId सत्यापित स्रोतों पर आधारित सामान्य कानूनी जानकारी देता है—यह कानूनी सलाह नहीं है। अपनी स्थिति से जुड़े निर्णयों के लिए किसी लाइसेंस प्राप्त अधिवक्ता से सलाह लें।",
  },
} as const;

/** Plain-language explanation of how data is handled and protected. */
export function PrivacyPage() {
  const language = useAppStore((state) => state.language);
  const copy = PAGE_COPY[language];

  return (
    <div className="space-y-10">
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />

      <Reveal className="flex items-start gap-3 rounded-xl border border-gold/30 bg-gold-soft/40 p-5">
        <Lock className="mt-0.5 size-5 shrink-0 text-gold-deep" />
        <div>
          <p className="font-semibold text-ink">{copy.reminderTitle}</p>
          <p className="mt-1 text-small leading-relaxed text-ink/90">{copy.reminder}</p>
        </div>
      </Reveal>

      <div className="grid gap-4 sm:grid-cols-2">
        {copy.sections.map((section, index) => {
          const Icon = SECTION_ICONS[index];
          return (
            <Reveal key={section.title} delay={index * 0.05}>
              <div className="flex h-full gap-4 rounded-xl border border-hairline bg-surface p-5">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
                  <Icon className="size-5" />
                </span>
                <div>
                  <h2 className="text-body font-semibold text-ink">{section.title}</h2>
                  <p className="mt-1 text-small leading-relaxed text-muted">{section.body}</p>
                </div>
              </div>
            </Reveal>
          );
        })}
      </div>

      <Reveal className="rounded-xl border border-teal/20 bg-teal/[0.04] p-6">
        <p className="flex items-center gap-2 font-display text-h4 text-teal">
          <ShieldCheck className="size-5 text-gold-deep" />
          {copy.noticeTitle}
        </p>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">{copy.noticeBody}</p>
      </Reveal>
    </div>
  );
}
