import { ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { useAppStore } from "@/store/appStore";

const PAGE_COPY = {
  en: {
    eyebrow: "How It Works",
    title: "A calm, source-grounded path from confusion to clarity",
    description:
      "LegalAId walks with you through eight steps—grounding every explanation in verified legal sources rather than guessing.",
    steps: [
      { title: "You tell us what happened", body: "Describe your situation in your own words—English, Hindi, or Hinglish. No legal terms needed." },
      { title: "We extract the facts", body: "The assistant pulls out the key details—what happened, where, how much, and when—and shows them back to you to correct." },
      { title: "We ask only what's missing", body: "If something important is unclear, you'll get a short, plain-language question instead of a legal form." },
      { title: "We find verified law", body: "Relevant provisions are retrieved from a verified corpus of Indian legal sources before anything is explained." },
      { title: "We check whether it applies", body: "Each provision is weighed against your specific facts and jurisdiction—not applied blindly." },
      { title: "We explain your rights", body: "You get a calm, plain-language summary of what the law may mean for you, with the reasoning shown openly." },
      { title: "We show useful evidence and next steps", body: "A checklist of documents that may strengthen your case, and a clear roadmap of what you can do next." },
      { title: "We prepare your draft", body: "When you're ready, generate an editable draft document grounded in your verified case details." },
    ],
    noticeTitle: "AI does not decide what the law is",
    noticeBody:
      "LegalAId uses a verified legal knowledge system to retrieve and check real legal sources before anything is presented to you. The AI's role is to explain—clearly and honestly—never to invent provisions or fill gaps with guesses. When information is insufficient, it says so.",
  },
  hi: {
    eyebrow: "यह कैसे काम करता है",
    title: "उलझन से स्पष्टता तक एक शांत, सत्यापित-स्रोत आधारित रास्ता",
    description:
      "LegalAId आठ चरणों में आपका साथ देता है और अनुमान लगाने के बजाय हर व्याख्या को सत्यापित कानूनी स्रोतों पर आधारित रखता है।",
    steps: [
      { title: "आप हमें बताते हैं कि क्या हुआ", body: "अपनी स्थिति अपने शब्दों में बताएँ—अंग्रेज़ी, हिंदी या हिंग्लिश में। कानूनी शब्द जानना ज़रूरी नहीं है।" },
      { title: "हम मुख्य तथ्य पहचानते हैं", body: "सहायक क्या हुआ, कहाँ हुआ, कितनी राशि जुड़ी है और कब हुआ जैसी मुख्य जानकारी पहचानकर आपको सुधारने के लिए दिखाता है।" },
      { title: "हम केवल छूटी हुई जानकारी पूछते हैं", body: "यदि कोई ज़रूरी बात स्पष्ट नहीं है, तो कानूनी फ़ॉर्म के बजाय आपसे एक छोटा और सरल सवाल पूछा जाता है।" },
      { title: "हम सत्यापित कानून खोजते हैं", body: "कुछ भी समझाने से पहले भारतीय कानूनी स्रोतों के सत्यापित संग्रह से संबंधित प्रावधान खोजे जाते हैं।" },
      { title: "हम जाँचते हैं कि कानून लागू होता है या नहीं", body: "हर प्रावधान को आपकी विशेष परिस्थितियों और क्षेत्राधिकार के आधार पर परखा जाता है—उसे बिना जाँच के लागू नहीं किया जाता।" },
      { title: "हम आपके अधिकार समझाते हैं", body: "आपको सरल भाषा में बताया जाता है कि कानून आपकी स्थिति के लिए क्या मायने रख सकता है, और उसका कारण भी स्पष्ट रूप से दिखाया जाता है।" },
      { title: "हम उपयोगी साक्ष्य और अगले कदम दिखाते हैं", body: "आपके मामले को मज़बूत करने वाले दस्तावेज़ों की सूची और आगे क्या करना है उसका स्पष्ट मार्ग मिलता है।" },
      { title: "हम आपका मसौदा तैयार करते हैं", body: "जब आप तैयार हों, तो अपने सत्यापित मामले की जानकारी पर आधारित संपादन योग्य दस्तावेज़ का मसौदा बनाएँ।" },
    ],
    noticeTitle: "AI यह तय नहीं करता कि कानून क्या है",
    noticeBody:
      "LegalAId किसी भी जानकारी को दिखाने से पहले वास्तविक कानूनी स्रोत खोजने और जाँचने के लिए सत्यापित कानूनी ज्ञान प्रणाली का उपयोग करता है। AI की भूमिका स्पष्ट और ईमानदार तरीके से समझाना है—प्रावधान गढ़ना या अनुमान से खाली जगह भरना नहीं। जानकारी पर्याप्त न होने पर यह साफ़ बताता है।",
  },
} as const;

export function HowItWorksPage() {
  const language = useAppStore((s) => s.language);
  const copy = PAGE_COPY[language];

  return (
    <div className="space-y-10">
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />

      <ol className="relative space-y-0">
        {copy.steps.map((step, i) => {
          const last = i === copy.steps.length - 1;
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
          {copy.noticeTitle}
        </p>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">{copy.noticeBody}</p>
      </Reveal>
    </div>
  );
}
