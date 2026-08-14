import { Link } from "react-router-dom";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";
import { useAppStore } from "@/store/appStore";

export function Footer() {
  const year = new Date().getFullYear();
  const language = useAppStore((s) => s.language);
  const hi = language === "hi";
  return (
    <footer className="mt-16 border-t border-hairline pt-8">
      <div className="space-y-6">
        <DisclaimerBanner />
        <div className="flex flex-col gap-3 text-tiny text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {year} LegalAId ·{" "}
            {hi
              ? "भारत में पहली बार कानूनी प्रक्रिया से जुड़ने वालों के लिए बनाया गया।"
              : "Built for first-time litigants in India."}
          </p>
          <nav className="flex flex-wrap items-center gap-x-5 gap-y-2" aria-label={hi ? "पादलेख" : "Footer"}>
            <Link to="/how-it-works" className="transition-colors hover:text-ink">
              {hi ? "यह कैसे काम करता है" : "How it works"}
            </Link>
            <Link to="/about" className="transition-colors hover:text-ink">
              {hi ? "परिचय" : "About"}
            </Link>
            <Link to="/privacy" className="transition-colors hover:text-ink">
              {hi ? "गोपनीयता और सुरक्षा" : "Privacy & Safety"}
            </Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
