import { useAppStore } from "@/store/appStore";
import type { Language } from "@/types";

/**
 * Lightweight bilingual copy for the primary assistant flow and shared UI.
 * (A full i18n framework is intentionally avoided — this app's Hindi surface is
 * focused and hand-tuned rather than machine-translated everywhere.)
 */
export const COPY = {
  en: {
    "hero.eyebrow": "A calmer way to begin",
    "hero.titleLead": "Tell us what",
    "hero.titleHighlight": "happened.",
    "hero.subtitle":
      "Describe your legal problem in your own words. You can write in English, Hindi, or Hinglish.",
    "hero.flow": "Your rights → Relevant law → Evidence → Next steps",
    "input.title": "Tell us what happened",
    "input.hint": "You don't need to know the law. Just explain what happened.",
    "input.placeholder":
      "My landlord has not returned my ₹20,000 security deposit even though I moved out two months ago.",
    "input.speak": "Speak",
    "input.analyze": "Analyze my situation",
    "input.analyzing": "Analyzing…",
    "input.tooShort": "Please add a little more detail so we can understand your situation.",
    "examples.title": "Not sure what to write?",
    "common.retry": "Try again",
    "common.back": "Back",
    "common.loading": "Loading…",
    "common.save": "Save changes",
    "common.saved": "Saved",
    "common.edit": "Edit",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.open": "Open",
    "common.download": "Download",
    "common.close": "Close",
    "status.ready": "Assistant ready",
    "status.checking": "Checking…",
    "status.offline": "Assistant offline",
    "nav.privacy": "Privacy & Safety",
  },
  hi: {
    "hero.eyebrow": "शुरुआत का एक शांत तरीका",
    "hero.titleLead": "बताइए क्या",
    "hero.titleHighlight": "हुआ।",
    "hero.subtitle":
      "अपनी कानूनी समस्या अपने शब्दों में बताइए। आप अंग्रेज़ी, हिंदी या हिंग्लिश में लिख सकते हैं।",
    "hero.flow": "आपके अधिकार → संबंधित कानून → साक्ष्य → अगले कदम",
    "input.title": "बताइए क्या हुआ",
    "input.hint": "आपको कानून जानने की ज़रूरत नहीं है। बस बताइए क्या हुआ।",
    "input.placeholder":
      "मैं दो महीने पहले घर छोड़ चुका/चुकी हूँ, फिर भी मकान मालिक ने मेरी ₹20,000 सिक्योरिटी वापस नहीं की।",
    "input.speak": "बोलें",
    "input.analyze": "मेरी स्थिति जाँचें",
    "input.analyzing": "जाँच हो रही है…",
    "input.tooShort": "कृपया थोड़ा और विवरण जोड़ें ताकि हम आपकी स्थिति समझ सकें।",
    "examples.title": "समझ नहीं आ रहा क्या लिखें?",
    "common.retry": "फिर कोशिश करें",
    "common.back": "वापस",
    "common.loading": "लोड हो रहा है…",
    "common.save": "बदलाव सहेजें",
    "common.saved": "सहेजा गया",
    "common.edit": "संपादित करें",
    "common.cancel": "रद्द करें",
    "common.delete": "हटाएँ",
    "common.open": "खोलें",
    "common.download": "डाउनलोड",
    "common.close": "बंद करें",
    "status.ready": "सहायक तैयार है",
    "status.checking": "जाँच हो रही है…",
    "status.offline": "सहायक ऑफ़लाइन है",
    "nav.privacy": "गोपनीयता और सुरक्षा",
  },
} as const;

export type CopyKey = keyof (typeof COPY)["en"];

export function translate(lang: Language, key: CopyKey): string {
  return COPY[lang]?.[key] ?? COPY.en[key];
}

/** Hook: returns a translator bound to the current language. */
export function useT(): { t: (key: CopyKey) => string; lang: Language } {
  const lang = useAppStore((s) => s.language);
  return { t: (key: CopyKey) => translate(lang, key), lang };
}
