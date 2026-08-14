import { NavLink } from "react-router-dom";
import { NAV_ITEMS } from "@/lib/constants";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";
import { BrandMark } from "@/components/common/BrandMark";
import { StatusPill } from "@/components/common/StatusPill";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ShieldCheck } from "lucide-react";
import { useT } from "@/lib/i18n";

/**
 * Persistent desktop navigation rail (Part 5). Hidden below the md breakpoint,
 * where the mobile top-bar + drawer take over.
 */
export function Sidebar() {
  const language = useAppStore((s) => s.language);
  const { t } = useT();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-sidebar flex-col border-r border-hairline bg-surface md:flex">
      <div className="px-6 py-6">
        <NavLink to="/" aria-label={language === "hi" ? "LegalAId होम" : "LegalAId home"} className="inline-flex rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal">
          <BrandMark />
        </NavLink>
      </div>

      <nav className="flex-1 space-y-1 px-3" aria-label={language === "hi" ? "मुख्य" : "Primary"}>
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
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-small font-medium transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-surface",
                  isActive ? "bg-teal/[0.07] text-teal" : "text-muted hover:bg-teal/[0.04] hover:text-ink",
                )
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={cn(
                      "absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-gold transition-opacity",
                      isActive ? "opacity-100" : "opacity-0",
                    )}
                    aria-hidden="true"
                  />
                  <Icon className="size-[1.15rem] shrink-0" strokeWidth={1.8} />
                  <span className={cn(language === "hi" && "font-deva")}>{label}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="space-y-4 border-t border-hairline px-5 py-5">
        <StatusPill />
        <NavLink
          to="/privacy"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-2 rounded-md text-tiny font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal",
              isActive ? "text-teal" : "text-muted hover:text-ink",
            )
          }
        >
          <ShieldCheck className="size-3.5 text-success" strokeWidth={1.9} />
          <span className={cn(language === "hi" && "font-deva")}>{t("nav.privacy")}</span>
        </NavLink>
        <LanguageSwitcher />
      </div>
    </aside>
  );
}
