import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import * as Dialog from "@radix-ui/react-dialog";
import { Menu, ShieldCheck, X } from "lucide-react";
import { NAV_ITEMS } from "@/lib/constants";
import { useAppStore } from "@/store/appStore";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { BrandMark } from "@/components/common/BrandMark";
import { StatusPill } from "@/components/common/StatusPill";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";

/**
 * Mobile navigation (Part 5, Part 33): a slim sticky top bar with a slide-in
 * drawer. No permanent sidebar on small screens.
 */
export function MobileNav() {
  const [open, setOpen] = useState(false);
  const language = useAppStore((s) => s.language);
  const { t } = useT();
  const location = useLocation();

  // Close the drawer whenever the route changes.
  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-hairline bg-surface/95 px-4 backdrop-blur md:hidden">
      <NavLink to="/" aria-label="LegalAId home" className="rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal">
        <BrandMark size="sm" />
      </NavLink>

      <div className="flex items-center gap-2">
        <StatusPill />
        <Dialog.Root open={open} onOpenChange={setOpen}>
          <Dialog.Trigger asChild>
            <button
              type="button"
              aria-label="Open menu"
              className="flex size-11 items-center justify-center rounded-lg text-ink transition-colors hover:bg-teal/[0.06] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal"
            >
              <Menu className="size-5" />
            </button>
          </Dialog.Trigger>

          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 z-40 bg-teal-900/40 backdrop-blur-[2px] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
            <Dialog.Content
              className={cn(
                "fixed inset-y-0 right-0 z-50 flex w-[19rem] max-w-[85vw] flex-col bg-surface shadow-lift focus:outline-none",
                "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right",
              )}
            >
              <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
                <Dialog.Title asChild>
                  <BrandMark size="sm" />
                </Dialog.Title>
                <Dialog.Close
                  aria-label="Close menu"
                  className="flex size-9 items-center justify-center rounded-lg text-muted transition-colors hover:bg-teal/[0.06] hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal"
                >
                  <X className="size-5" />
                </Dialog.Close>
              </div>

              <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Primary">
                {NAV_ITEMS.map((item) => {
                  const Icon = item.icon;
                  const label = language === "hi" ? item.labelHi : item.label;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.end}
                      className={({ isActive }) =>
                        cn(
                          "flex items-center gap-3 rounded-lg px-3 py-3 text-body font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal",
                          isActive ? "bg-teal/[0.07] text-teal" : "text-ink hover:bg-teal/[0.04]",
                        )
                      }
                    >
                      <Icon className="size-5 shrink-0" strokeWidth={1.8} />
                      <span className={cn(language === "hi" && "font-deva")}>{label}</span>
                    </NavLink>
                  );
                })}
                <NavLink
                  to="/privacy"
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-lg px-3 py-3 text-body font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal",
                      isActive ? "bg-teal/[0.07] text-teal" : "text-ink hover:bg-teal/[0.04]",
                    )
                  }
                >
                  <ShieldCheck className="size-5 shrink-0 text-success" strokeWidth={1.8} />
                  <span className={cn(language === "hi" && "font-deva")}>{t("nav.privacy")}</span>
                </NavLink>
              </nav>

              <div className="border-t border-hairline px-5 py-4">
                <LanguageSwitcher />
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </div>
    </header>
  );
}
