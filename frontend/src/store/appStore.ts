import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Language } from "@/types";

interface AppState {
  language: Language;
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      language: "en",
      setLanguage: (language) => set({ language }),
      toggleLanguage: () => set({ language: get().language === "en" ? "hi" : "en" }),
    }),
    { name: "legalaid-app" },
  ),
);
