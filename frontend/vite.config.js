/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
// LegalAId frontend build + dev configuration.
// In dev, /api is proxied to the FastAPI backend so the browser makes
// same-origin requests (no CORS wildcard needed, no API base leaked to client).
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000",
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: "dist",
        sourcemap: false,
        target: "es2021",
        rollupOptions: {
            output: {
                manualChunks: {
                    "react-vendor": ["react", "react-dom", "react-router-dom"],
                    "query-vendor": ["@tanstack/react-query"],
                    "motion-vendor": ["framer-motion"],
                },
            },
        },
    },
    test: {
        globals: true,
        environment: "jsdom",
        setupFiles: ["./src/test/setup.ts"],
        css: false,
        include: ["src/**/*.{test,spec}.{ts,tsx}"],
    },
});
