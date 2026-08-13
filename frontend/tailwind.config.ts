import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

/**
 * LegalAId design tokens.
 *
 * Palette, type scale and motion are the source of truth for the whole app.
 * Colors are authored as raw hex (light-mode only product — "calm confidence"),
 * so Tailwind opacity modifiers (e.g. bg-teal/5) work everywhere.
 */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: "#123F3F", // Deep Teal — primary
          dark: "#0B3030", // Dark Teal — hover / deep surfaces
          700: "#123F3F",
          800: "#0B3030",
          900: "#082424",
        },
        ivory: {
          DEFAULT: "#F6F4EA", // Warm Ivory — app background
          soft: "#FCFBF6", // Soft Ivory — cards / raised surfaces
        },
        gold: {
          DEFAULT: "#E4A12D", // Legal Gold — emphasis / verification
          soft: "#F5E7C6",
          deep: "#B87E19",
        },
        ink: "#173636", // Dark Text
        muted: "#677A77", // Muted Text
        hairline: "#D9DDD4", // Border
        success: "#4F8F70",
        warning: "#D39A32",
        danger: "#C96B5C",
        // Semantic aliases used by primitives
        background: "#F6F4EA",
        surface: "#FCFBF6",
        foreground: "#173636",
      },
      borderColor: {
        DEFAULT: "#D9DDD4",
      },
      fontFamily: {
        display: ['"DM Serif Display"', "Georgia", "Cambria", "serif"],
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          '"Noto Sans Devanagari"',
          "sans-serif",
        ],
        deva: ['"Noto Sans Devanagari"', "Inter", "sans-serif"],
      },
      fontSize: {
        // [size, { lineHeight, letterSpacing }]
        "display-xl": ["4.5rem", { lineHeight: "1.03", letterSpacing: "-0.02em" }], // 72
        "display-lg": ["3.75rem", { lineHeight: "1.05", letterSpacing: "-0.02em" }], // 60
        display: ["3.5rem", { lineHeight: "1.06", letterSpacing: "-0.018em" }], // 56
        h1: ["3rem", { lineHeight: "1.1", letterSpacing: "-0.015em" }], // 48
        h2: ["2.25rem", { lineHeight: "1.15", letterSpacing: "-0.01em" }], // 36
        h3: ["1.5rem", { lineHeight: "1.25", letterSpacing: "-0.005em" }], // 24
        h4: ["1.25rem", { lineHeight: "1.3" }], // 20
        "body-lg": ["1.125rem", { lineHeight: "1.65" }], // 18
        body: ["1rem", { lineHeight: "1.62" }], // 16
        small: ["0.875rem", { lineHeight: "1.55" }], // 14
        tiny: ["0.8125rem", { lineHeight: "1.5" }], // 13
        eyebrow: ["0.75rem", { lineHeight: "1.4", letterSpacing: "0.14em" }], // 12
      },
      borderRadius: {
        sm: "8px",
        md: "10px",
        lg: "14px",
        xl: "18px",
        "2xl": "24px",
        "3xl": "32px",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(23,54,54,0.04), 0 10px 30px -18px rgba(23,54,54,0.14)",
        lift: "0 2px 6px rgba(23,54,54,0.05), 0 22px 48px -24px rgba(23,54,54,0.22)",
        ring: "0 0 0 4px rgba(18,63,63,0.12)",
        gold: "0 0 0 4px rgba(228,161,45,0.16)",
      },
      maxWidth: {
        content: "1180px",
        prose: "68ch",
        reading: "760px",
      },
      spacing: {
        sidebar: "17rem", // 272px desktop sidebar
        18: "4.5rem",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0", opacity: "0" },
          to: { height: "var(--radix-accordion-content-height)", opacity: "1" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)", opacity: "1" },
          to: { height: "0", opacity: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "rise-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.24s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.4s ease-out both",
        "rise-in": "rise-in 0.45s cubic-bezier(0.22,1,0.36,1) both",
      },
      transitionTimingFunction: {
        calm: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [animate],
} satisfies Config;
