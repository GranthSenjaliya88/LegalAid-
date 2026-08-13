export type LawStatus = "CURRENT" | "ACTIVE" | "HISTORICAL" | "REPEALED" | (string & {});

/** A single statutory match returned by retrieval / search (mirrors RetrievalMatch). */
export interface RetrievalMatch {
  act: string;
  section: string;
  title?: string | null;
  relevant_text: string;
  plain_language_summary?: string | null;
  confidence: number;
  source_reference?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  official_source_url?: string | null;
  source_authority?: string | null;
  source_type?: string | null;
  historical_reference?: string | null;
  state?: string | null;
  domain?: string | null;
  status?: LawStatus | null;
  last_verified?: string | null;
  verification_status?: string | null;
  why_applies?: string | null;
}

export interface RetrievalResponse {
  status: string;
  matches: RetrievalMatch[];
  state_verified: boolean;
  state_note?: string | null;
}

/* ---------------- Corpus (Legal Resources) ---------------- */

export interface CorpusStats {
  total_acts: number;
  total_sections: number;
  domains: Record<string, number>;
}

export interface CorpusAct {
  id: number;
  name: string;
  short_name: string;
  year: number;
  jurisdiction: string;
  domain: string;
  description?: string | null;
  source_url?: string | null;
  section_count: number;
}

export interface CorpusSection {
  id: number;
  act_id: number;
  act_short_name?: string;
  section_number: string;
  title?: string | null;
  text: string;
  domain: string;
  language: string;
}

export interface CorpusSearchResult {
  query: string;
  domain?: string | null;
  status: string;
  total: number;
  results: RetrievalMatch[];
}

/** Directory rows are dynamic DB rows; render defensively. */
export interface CorpusAuthority {
  id?: number;
  name?: string;
  domain?: string;
  jurisdiction?: string;
  website?: string;
  official_url?: string;
  helpline?: string;
  description?: string;
  [key: string]: unknown;
}

export interface CorpusJudgment {
  id?: number;
  case_name?: string;
  title?: string;
  citation?: string;
  court?: string;
  year?: number | string;
  summary?: string;
  domain?: string;
  url?: string;
  official_url?: string;
  [key: string]: unknown;
}

export interface CorpusVerifyIssue {
  check: string;
  severity: string;
  detail: string;
}

export interface CorpusVerifyReport {
  passed: boolean;
  summary: string;
  issues: CorpusVerifyIssue[];
}
