/**
 * LegalAId design tokens.
 *
 * Palette, type scale and motion are the source of truth for the whole app.
 * Colors are authored as raw hex (light-mode only product — "calm confidence"),
 * so Tailwind opacity modifiers (e.g. bg-teal/5) work everywhere.
 */
declare const _default: {
    content: string[];
    theme: {
        extend: {
            colors: {
                teal: {
                    DEFAULT: string;
                    dark: string;
                    700: string;
                    800: string;
                    900: string;
                };
                ivory: {
                    DEFAULT: string;
                    soft: string;
                };
                gold: {
                    DEFAULT: string;
                    soft: string;
                    deep: string;
                };
                ink: string;
                muted: string;
                hairline: string;
                success: string;
                warning: string;
                danger: string;
                background: string;
                surface: string;
                foreground: string;
            };
            borderColor: {
                DEFAULT: string;
            };
            fontFamily: {
                display: [string, string, string, string];
                sans: [string, string, string, string, string, string, string];
                deva: [string, string, string];
            };
            fontSize: {
                "display-xl": [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                "display-lg": [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                display: [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                h1: [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                h2: [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                h3: [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
                h4: [string, {
                    lineHeight: string;
                }];
                "body-lg": [string, {
                    lineHeight: string;
                }];
                body: [string, {
                    lineHeight: string;
                }];
                small: [string, {
                    lineHeight: string;
                }];
                tiny: [string, {
                    lineHeight: string;
                }];
                eyebrow: [string, {
                    lineHeight: string;
                    letterSpacing: string;
                }];
            };
            borderRadius: {
                sm: string;
                md: string;
                lg: string;
                xl: string;
                "2xl": string;
                "3xl": string;
            };
            boxShadow: {
                soft: string;
                lift: string;
                ring: string;
                gold: string;
            };
            maxWidth: {
                content: string;
                prose: string;
                reading: string;
            };
            spacing: {
                sidebar: string;
                18: string;
            };
            keyframes: {
                "accordion-down": {
                    from: {
                        height: string;
                        opacity: string;
                    };
                    to: {
                        height: string;
                        opacity: string;
                    };
                };
                "accordion-up": {
                    from: {
                        height: string;
                        opacity: string;
                    };
                    to: {
                        height: string;
                        opacity: string;
                    };
                };
                "fade-in": {
                    from: {
                        opacity: string;
                    };
                    to: {
                        opacity: string;
                    };
                };
                "rise-in": {
                    from: {
                        opacity: string;
                        transform: string;
                    };
                    to: {
                        opacity: string;
                        transform: string;
                    };
                };
                shimmer: {
                    "100%": {
                        transform: string;
                    };
                };
            };
            animation: {
                "accordion-down": string;
                "accordion-up": string;
                "fade-in": string;
                "rise-in": string;
            };
            transitionTimingFunction: {
                calm: string;
            };
        };
    };
    plugins: {
        handler: () => void;
    }[];
};
export default _default;
