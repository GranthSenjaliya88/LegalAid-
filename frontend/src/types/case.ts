/** Domains supported by the legal engine. */
export type Domain = "consumer" | "labor" | "tenant" | "cyber" | "criminal" | "general";

export type Language = "en" | "hi";

export type Urgency = "low" | "medium" | "high" | "urgent";

/** Lifecycle status persisted on the case. String-open to tolerate backend additions. */
export type CaseStatus =
  | "new"
  | "classified"
  | "retrieved"
  | "clarified"
  | "explained"
  | "documented"
  | (string & {});

/** Structured facts extracted from the user's description (mirrors CaseFactsData). */
export interface CaseFacts {
  parties?: string | null;
  incident?: string | null;
  date?: string | null;
  location?: string | null;
  state?: string | null;
  subdomain?: string | null;
  amount?: string | number | null;
  agreement_exists?: boolean | null;
  notice_given?: boolean | null;
  desired_outcome?: string | null;
  urgency?: Urgency | null;
  additional_facts?: string | null;
}

/** POST /api/cases */
export interface CreateCaseRequest {
  text: string;
  language?: Language;
  session_id?: string;
}

export interface CreateCaseResponse {
  case_id: string;
  language: string;
  status: string;
  created_at?: string;
}

/** GET /api/cases/{id} */
export interface CaseState {
  case_id: string;
  session_id?: string | null;
  language: string;
  original_text: string;
  domain?: Domain | null;
  subdomain?: string | null;
  state?: string | null;
  urgency: Urgency;
  status: CaseStatus;
  created_at: string;
  facts?: CaseFacts | null;
}
