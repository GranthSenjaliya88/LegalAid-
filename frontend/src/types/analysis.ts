import type { CaseFacts, Domain, Urgency } from "./case";

export type Confidence = "HIGH" | "MEDIUM" | "LOW" | "INSUFFICIENT INFORMATION" | (string & {});

/** POST /api/cases/{id}/classify */
export interface ClassifyResponse {
  case_id?: string;
  domain: Domain;
  subdomain?: string | null;
  confidence: number;
  jurisdiction_required: boolean;
  urgency: Urgency;
  facts: CaseFacts;
}

/** POST /api/cases/{id}/clarify */
export interface ClarifyResponse {
  needs_clarification: boolean;
  questions: string[];
  missing_facts: string[];
}

/** Value type accepted by clarify/respond — backend merges these into CaseFacts. */
export type AnswerValue = string | number | boolean | null;

/** POST /api/cases/{id}/clarify/respond */
export interface ClarifyRequest {
  answers: Record<string, AnswerValue>;
}

export interface CitationDetail {
  act: string;
  section: string;
  source_reference?: string | null;
}

export interface RightExplanation {
  explanation: string;
  why_applies?: string | null;
  citations: CitationDetail[];
}

/** Reasoning map node (explainer emits {step, status, detail}). */
export interface ReasoningStep {
  step: string;
  status: string;
  detail: string;
}

/** "Why this law" entry (also reused for relevant_law). */
export interface WhyThisLaw {
  act: string;
  section: string;
  title?: string | null;
  status: string;
  source_badge?: string;
  applicability_status?: string;
  matching_factors?: string[];
  why_applies?: string;
  official_source_url?: string | null;
  source_authority?: string;
}

export interface WhyNotThisLaw {
  law: string;
  status: string;
  reason: string;
}

/** Compact comparison entry embedded in the explanation. */
export interface LawComparisonEntry {
  law: string;
  applies: string;
  reason: string;
}

export interface ClaimVerification {
  claim?: string;
  supported?: boolean;
  citation?: string;
  status?: string;
  [key: string]: unknown;
}

export interface VerificationCard {
  claims_checked: number;
  sources_verified: number;
  unsupported_claims: number;
  confidence_badge: Confidence;
  status_note?: string;
  claim_verification_list?: ClaimVerification[];
}

/** Emergency plan is a loosely-typed dict from the backend; render defensively. */
export interface EmergencyPlan {
  is_urgent?: boolean;
  title?: string;
  message?: string;
  warning?: string;
  immediate_steps?: string[];
  steps?: string[];
  preserve_evidence?: string[];
  reporting_path?: string;
  source?: string | null;
  [key: string]: unknown;
}

/** POST /api/cases/{id}/explain */
export interface ExplainResponse {
  summary: string;
  what_we_understood?: string | null;
  possible_rights: string[];
  relevant_law: WhyThisLaw[];
  what_is_uncertain?: string | null;
  documents_that_may_help: string[];
  rights: RightExplanation[];
  next_steps: string[];
  reasoning_map: ReasoningStep[];
  why_this_law: WhyThisLaw[];
  why_not_this_law: WhyNotThisLaw[];
  emergency_plan?: EmergencyPlan | null;
  verification_card?: VerificationCard | null;
  law_comparison_table: LawComparisonEntry[];
  confidence: Confidence;
  disclaimer?: string | null;
}

/* ----- Evidence ----- */
export type EvidenceImportance = "essential" | "supporting" | (string & {});

export interface EvidenceItem {
  document_name: string;
  importance: EvidenceImportance;
  why_it_matters: string;
  available: boolean;
}

export interface EvidenceResponse {
  claim_summary: string;
  checklist: EvidenceItem[];
}

/* ----- Action roadmap ----- */
export interface ActionStep {
  step_number: number;
  title: string;
  description: string;
  required_document?: string | null;
  next_action?: string | null;
}

export interface ActionRoadmapResponse {
  urgency: Urgency;
  urgent_warning?: string | null;
  steps: ActionStep[];
}

/* ----- Verification ----- */
export interface VerificationItem {
  citation_text: string;
  act_exists: boolean;
  section_exists: boolean;
  retrieved_in_case: boolean;
  text_matches: boolean;
  format_valid: boolean;
  is_valid: boolean;
  status_note: string;
}

export interface VerifyResponse {
  all_verified: boolean;
  total_citations: number;
  verified_count: number;
  unsupported_count: number;
  items: VerificationItem[];
}

/* ----- Applicability + comparison (dedicated endpoints) ----- */
export interface ApplicabilityEvaluation {
  section_id?: number | null;
  act_name: string;
  section_number: string;
  applicability_status: string;
  matching_factors: string[];
  missing_factors: string[];
  disqualifying_factors: string[];
  applicability_reason: string;
}

export interface ApplicabilityResponse {
  case_id: string;
  evaluations: ApplicabilityEvaluation[];
}

export interface LawComparisonRow {
  law_title: string;
  status: string;
  applicability: string;
  reason: string;
}

export interface CompareResponse {
  case_id: string;
  rows: LawComparisonRow[];
}
