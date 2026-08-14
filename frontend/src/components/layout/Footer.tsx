import { Link } from "react-router-dom";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="mt-16 border-t border-hairline pt-8">
      <div className="space-y-6">
        <DisclaimerBanner />
        <div className="flex flex-col gap-3 text-tiny text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>© {year} LegalAId · Built for first-time litigants in India.</p>
          <nav className="flex flex-wrap items-center gap-x-5 gap-y-2" aria-label="Footer">
            <Link to="/how-it-works" className="transition-colors hover:text-ink">
              How it works
            </Link>
            <Link to="/about" className="transition-colors hover:text-ink">
              About
            </Link>
            <Link to="/privacy" className="transition-colors hover:text-ink">
              Privacy &amp; Safety
            </Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
