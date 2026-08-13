export type DocumentType =
  | "complaint"
  | "consumer_complaint"
  | "labor_complaint"
  | "tenant_notice"
  | "legal_notice"
  | (string & {});

export interface DocumentSection {
  id: string;
  title: string;
  content: string;
}

/** POST /api/cases/{id}/document · GET/PUT /api/documents/{id} */
export interface DocumentData {
  document_id: string;
  case_id: string;
  type: DocumentType;
  title: string;
  sections: DocumentSection[];
  quality_score: number;
  quality_warnings: string[];
  disclaimer: string;
  created_at: string;
}

export interface UpdateDocumentRequest {
  title?: string;
  sections: DocumentSection[];
}
