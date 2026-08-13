import { type ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { MobileNav } from "./MobileNav";
import { Footer } from "./Footer";

/**
 * Top-level application frame. Persistent sidebar on desktop, sticky top bar +
 * drawer on mobile. The main column is width-constrained for comfortable
 * reading and always leaves room for the fixed sidebar on md+.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-ivory">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-teal focus:px-4 focus:py-2 focus:text-small focus:font-medium focus:text-ivory-soft focus:shadow-lift"
      >
        Skip to content
      </a>
      <Sidebar />
      <MobileNav />
      <div className="flex min-h-screen flex-col md:pl-sidebar">
        <main id="main" tabIndex={-1} className="flex-1 outline-none">
          <div className="mx-auto w-full max-w-content px-5 py-8 sm:px-8 sm:py-10 lg:px-12">
            {children}
            <Footer />
          </div>
        </main>
      </div>
    </div>
  );
}
