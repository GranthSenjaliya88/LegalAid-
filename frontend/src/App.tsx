import { useEffect } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AppShell } from "@/components/layout/AppShell";
import { HomePage } from "@/pages/HomePage";
import { CaseWorkspacePage } from "@/pages/CaseWorkspacePage";
import { ResourcesPage } from "@/pages/ResourcesPage";
import { CasesPage } from "@/pages/CasesPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { DocumentEditorPage } from "@/pages/DocumentEditorPage";
import { HowItWorksPage } from "@/pages/HowItWorksPage";
import { AboutPage } from "@/pages/AboutPage";
import { PrivacyPage } from "@/pages/PrivacyPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

import { CorpusDashboardPage } from "@/pages/CorpusDashboardPage";

/**
 * Resets scroll position and moves focus to the main region on navigation, so
 * keyboard and screen-reader users start each page at the top (Part 31, a11y).
 */
function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
    // Move focus to the main landmark without stealing it on first paint.
    const main = document.getElementById("main");
    if (main) main.focus({ preventScroll: true });
  }, [pathname]);
  return null;
}

/**
 * Application root. Wires global providers (React Query, tooltips, toasts) and
 * the client-side router. All routes render inside the persistent AppShell so
 * navigation, header status, and footer stay mounted across pages (Part 5).
 */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={200}>
        <BrowserRouter>
          <ScrollToTop />
          <AppShell>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/case/:id" element={<CaseWorkspacePage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/admin/corpus-dashboard" element={<CorpusDashboardPage />} />
              <Route path="/cases" element={<CasesPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/documents/:id" element={<DocumentEditorPage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </AppShell>
          <Toaster />
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
