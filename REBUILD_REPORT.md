# LegalAId — Production Rebuild Report

**Project:** LegalAId — AI Legal Rights Assistant for First-Generation Litigants in India
**Date:** 2026-08-12
**Scope:** Frontend-first phased rebuild (Vite + React + TypeScript) wired to the existing FastAPI backend, followed by backend cleanup, database hardening, and grounding/security review.

---

## 1. Executive summary

The rebuild followed the mandatory phased order: audit first, then the React architecture and design system, all screens with loading/empty/error states, reusable components, animation + responsive/a11y polish, a typed API contract, backend refactor, database schema hardening with safe migrations, retrieval/AI-grounding hardening, and finally frontend↔backend integration and this audit.

No working legal logic was thrown away. The retrieval-before-generation pipeline (database is the source of truth for statute sections; the LLM never invents section numbers) is intact and was hardened rather than replaced. Every change was made against the real runtime shapes in the codebase — types, hooks, services, stores, and ORM models were read before editing.

Five substantive defects were found and fixed, three of which would cause live 500s or silently degrade legal-retrieval quality. The database FTS index was corrupted (roughly 4× duplicate/orphan rows) and has been rebuilt and verified 1:1 with the source table. Security was hardened per the Part 30 requirements: CORS locked to explicit origins, production error bodies redacted, and log redaction strengthened so OTPs, passwords, PINs, card and account numbers never reach the logs.

**Honest limitation (read this):** the sandbox blocks both the npm registry and PyPI (both return HTTP 403 through the proxy). As a result `npm install`, `vite build`, `tsc`, `vitest`, `pip install`, and `pytest` **could not be executed**. Success is therefore **not** claimed on the basis of a green build or a passing test suite. Instead, verification was done with everything that *can* run offline: `py_compile`/`compileall`, custom AST scans for undefined names, import/export/dependency resolution across the frontend, direct `sqlite3` integrity/count/trigger tests against the live database, and a unit test of the log-redaction filter. Section 7 lists exactly what was and was not run, and Section 9 lists the commands to run once registry access is restored.

---

## 2. What changed, by phase

### Phase 1 — Audit
Catalogued the active application graph. The live app is `backend/app/main.py` mounting `app/api/routes/*`, using the `app/schemas/` package, `app/db/database.py`, and the service layer under `app/services/` and `app/legal/`. Identified (but did not delete) a dead-code cluster that the running app never imports — see Section 8.

### Phases 2–5 — Frontend architecture, screens, components, polish
Vite + React 18 + TypeScript SPA with a `@`→`src` path alias and a dev proxy from `/api` to the backend (`http://127.0.0.1:8000`, overridable via `VITE_PROXY_TARGET`). Styling is Tailwind v3.4 (light mode) with hand-authored shadcn-style primitives (Radix + `cva` + a `cn` helper); Framer Motion for animation; React Hook Form + Zod for forms; TanStack Query v5 for server state; Zustand v5 (persisted) for client state; react-router-dom v6; sonner for toasts.

The application root (`src/App.tsx`) wires all providers and the router, and includes an accessibility affordance: on every route change `ScrollToTop` returns the window to the top and moves focus to `<main id="main">`, which was made focusable (`tabIndex={-1}`) so the skip-link and post-navigation focus both land correctly. All screens carry explicit loading, empty, and error states. The design tokens are unchanged from the established system (teal `#123F3F`, ivory `#F6F4EA`, gold `#E4A12D` reserved for verification/emphasis; DM Serif Display / Inter / Noto Sans Devanagari; the `ease-calm` curve).

### Phase 6 — Typed API contract
The API client unwraps the backend envelope consistently: `{success: true, data}` returns `data`; `{success: false, error: {code, message}}` throws a typed `ApiError` carrying code + HTTP status; non-OK responses and network/abort errors are normalised to the same `ApiError` shape; PDF responses take a blob path. This was read end-to-end and confirmed against the backend's actual response shapes.

### Phase 7 — Backend refactor + bug fixes
See Section 3 — this is where the fact-loss helper and the two missing-import defects were fixed, plus the security hardening.

### Phase 8 — Database schema hardening + safe migrations
Per Part 35 the database was **backed up before any migration** to `backend/data/backups/legalaid-20260812-195037.db`, and the original database was **not deleted**. Idempotent column migrations (`_apply_migrations`) add missing columns to `acts`, `sections`, and `case_facts` without touching existing data. Record counts were validated after the work (Section 6).

### Phase 9 — Retrieval + AI grounding
Confirmed the pipeline retrieves from the database corpus before any generation and that citations are verified against stored acts/sections. Rebuilt the FTS index so BM25 scoring operates over the correct corpus size (Section 3). Strengthened log redaction (Section 4).

### Phase 10 — Integration
Confirmed the frontend data layer and the backend envelope agree on success and error shapes, so real error codes/messages surface to the UI rather than generic failures.

---

## 3. Bugs fixed (with evidence)

**1. Fact-loss across the analysis pipeline (high impact).**
Ten routes in `app/api/routes/analysis.py` rebuilt the case "facts" dict from only a handful of fields, dropping `date`, `location`, `desired_outcome`, `subdomain`, and `additional_facts`. Because `update_facts_from_answers` only merges keys that are present, anything not reconstructed was absent from the dict handed to retrieval — so answering clarifying questions could *degrade* retrieval instead of improving it. Fixed with a single `_facts_to_dict(case)` helper that reads every known fact field plus case-level fallbacks (incident←`original_text`, `state`, `subdomain`), now used by all analysis phases. *Evidence:* all fact dicts in the file route through the helper; the file compiles; an AST scan reports zero undefined names.

**2. Missing `import json` in `app/api/routes/legal.py` (live 500).**
`/procedures` and `/concepts` called `json.loads` without importing `json`, so those endpoints raised `NameError` at request time. Fixed by adding the import. *Evidence:* file compiles; AST scan clean.

**3. Missing `import json` in `app/legal/corpus_search.py` (live 500).**
The same defect in the retrieval corpus-search path (three `json.loads` calls). Found via a custom AST scan that flags stdlib names used but never imported. Fixed. *Evidence:* file compiles; AST scan clean.

**4. FTS index corruption (retrieval quality).**
`sections_fts` held ~338 rows against 82 active sections — roughly 4× duplicates plus orphan rows with no matching section. Orphans inflate the BM25 corpus statistics and never join back (retrieval joins `sections s ON s.id = fts.rowid`), skewing ranking. Root cause: the INSERT trigger never pinned `rowid = sections.id`, and the contentless-table DELETE/UPDATE triggers used a plain `DELETE`, which this SQLite build rejects for `content=''` tables. Fixed by rewriting the triggers to pin `rowid = new.id` on insert and to use the special `'delete'` command form on delete/update, plus a self-contained `rebuild_fts.py` (raw `sqlite3`, no app imports, so it runs despite the blocked package registry) that drops and rebuilds the index and verifies the result. *Evidence:* after rebuild, `sections_fts` = 82, distinct rowids = 82, orphan rows = 0, and a `MATCH` probe returns rows; current live counts show **sections=82, fts=82** (Section 6).

**5. Insecure CORS + leaky error bodies (Part 30).**
CORS was `["*"]` combined with `allow_credentials=True`, an invalid and insecure combination. Fixed to explicit, environment-driven origins (defaulting to the dev frontend) with an explicit method/header allow-list. The global exception handler now redacts internal error detail in production (`ENVIRONMENT`/`is_production`) while keeping full detail in development. *Evidence:* `app/main.py`, `app/core/config.py` compile; behaviour confirmed by reading the handler and settings.

---

## 4. Security review (Part 30)

**No secrets in the frontend.** The AI/model keys live only in backend configuration; the client talks to the backend, never directly to the model provider.

**Log redaction — "never log OTP, password, PIN, bank password, or full payment credentials."** The `PrivacyFilter` in `app/core/logging.py` was strengthened to (a) fully redact any log line mentioning `AI_API_KEY`/`GEMINI_API_KEY`; (b) mask values following a sensitive key — `password/passwd/pwd/otp/pin/cvv/cvc/secret/token/api_key/authorization/auth/bank_password/card_number/account_number` — in `key: value`, `key=value`, and `"key": "value"` forms; and (c) mask 12–19-digit runs that look like card or account numbers (spaces/dashes tolerated). It was unit-tested offline: lines containing a password, an OTP, a PIN, and a card number were redacted, while a benign `amount: 50000` was left untouched.

**CORS + error redaction.** Explicit origins (no wildcard with credentials); production error responses redacted (see Bug 5).

**Retrieval-side injection resistance.** The LLM is never the source of truth for statute sections — sections come from the database and citations are verified against stored acts/sections — which structurally limits prompt-injection influence over the legal content that reaches the user.

**UI privacy reminder.** The interface advises users not to enter passwords, OTPs, PINs, or unnecessary sensitive information.

**Residual items (not yet implemented — recommended):** application-level rate limiting and a secure-deletion path for user case data are recommended as follow-ups; both are noted in Section 9.

---

## 5. Accessibility & performance notes

**Accessibility.** Focus is moved to `<main>` after each navigation and the main region is focusable so the skip link works; the app is built light-mode with the established token contrast; Devanagari is a first-class font for Hindi content; interactive primitives are Radix-based (keyboard and ARIA semantics come from the primitive). A full automated a11y pass (axe) is pending toolchain access.

**Performance.** SPA with route-level structure and TanStack Query caching to avoid redundant refetches; FTS/BM25 retrieval now runs over the correct (de-duplicated) corpus, which both speeds scoring and improves ranking. A production `vite build` bundle-size/perf measurement is pending toolchain access.

---

## 6. Database state (post-work, verified)

`PRAGMA integrity_check` → **ok**. Live counts:

| Table | Count |
|---|---|
| acts | 26 |
| sections | 82 |
| sections_fts | 82 (0 orphans, distinct rowids = 82) |
| cases | 432 |
| case_facts | 432 |
| documents | 98 |

Part 35 compliance: pre-migration backup at `backend/data/backups/legalaid-20260812-195037.db` (present, 1,052,672 bytes); the original `backend/data/legalaid.db` was not deleted; record counts preserved.

---

## 7. Verification performed — and what could not be run

**Ran successfully (offline):**
- `python3 -m compileall app rebuild_fts.py seed.py` → exit 0 (whole backend byte-compiles).
- `py_compile` on each edited file (`main.py`, `analysis.py`, `legal.py`, `corpus_search.py`, `config.py`, `logging.py`, `database.py`) → OK.
- Custom AST scan for names used-but-not-imported across `app/` → zero undefined names (this is how the second missing-`json` import was caught).
- Frontend static resolution: every `@/` import resolves to a file that exports the imported symbol; all relative imports resolve; every imported package is declared in `package.json`.
- Database: `integrity_check` = ok; FTS row-count / distinct-rowid / orphan checks; a `MATCH` probe; table counts.
- FTS triggers tested empirically on a database copy: INSERT/UPDATE/DELETE all succeed with the corrected contentless-table trigger forms.
- `PrivacyFilter` unit-tested with realistic messages (password/OTP/PIN/card redacted; benign amount preserved).

**Could NOT be run (environment blocks the package registries — npm and PyPI both return HTTP 403 through the proxy):**
- `npm install`, `npm run build` (Vite production build), `tsc` (full type-check), `vitest` (frontend unit/component tests).
- `pip install` of backend runtime deps (fastapi, sqlalchemy, google-generativeai, reportlab), and therefore `pytest` and any test that imports the FastAPI app or hits live endpoints.

Because of this, **no claim is made that the project builds, type-checks, or passes an automated test suite.** The checks above validate syntax, name resolution, import/export wiring, dependency declarations, and database/log behaviour — not a running production build.

---

## 8. Dead code (identified, intentionally NOT deleted)

The following are not imported by the running app (`main.py` uses `api/routes/*`, the `schemas/` package, and `db/database.py`): `app/api/cases.py`, `app/api/corpus.py`, `app/agents/*`, the flat `app/schemas.py`, and the flat `app/database.py`. These were left in place to honour "don't throw away working logic" and to avoid a risky deletion without a runnable test suite to confirm nothing regresses. Removing them is safe to do once tests can run — see Section 9.

---

## 9. Recommended next steps

Once package-registry access is restored:

1. `cd frontend && npm install && npm run build && npx tsc --noEmit && npx vitest run` — confirm the production build, full type-check, and frontend tests are green.
2. `cd backend && pip install -r requirements.txt && pytest` — install runtime deps and run the backend suite (add endpoint tests for `/procedures`, `/concepts`, and the clarify→re-retrieve path, which exercise the three fixed defects).
3. Run an automated accessibility pass (axe) against the built frontend and capture a production bundle-size/perf measurement.
4. Add application-level rate limiting and a secure user-data deletion path (the two residual Part 30 items).
5. After the suite is green, remove the dead-code cluster in Section 8 in a single isolated commit and re-run tests.

---

## 10. Files touched (this rebuild)

**Frontend (created/edited):** `src/App.tsx`, `src/main.tsx`, `src/components/layout/AppShell.tsx`, `src/pages/NotFoundPage.tsx`, plus the screens, primitives, data layer, and configuration established across Phases 2–6.

**Backend (edited):** `app/api/routes/analysis.py` (fact-loss helper), `app/api/routes/legal.py` (import fix), `app/legal/corpus_search.py` (import fix), `app/core/config.py` (environment + CORS parsing), `app/main.py` (CORS allow-list + production error redaction), `app/core/logging.py` (privacy filter), `app/db/database.py` (FTS DDL + contentless-table triggers).

**Backend (added):** `rebuild_fts.py` (self-contained FTS rebuild + verification).

**Database:** backup created at `backend/data/backups/legalaid-20260812-195037.db`; FTS index rebuilt in `backend/data/legalaid.db`.
