import type { LucideIcon } from "lucide-react";
import {
  ShoppingBag,
  Briefcase,
  KeyRound,
  ShieldAlert,
  Gavel,
  Scale,
  Sparkles,
  FolderClosed,
  FileText,
  Compass,
  Info,
} from "lucide-react";
import type { Domain } from "@/types";

/* ------------------------------------------------------------------ *
 * Domains
 * ------------------------------------------------------------------ */
export interface DomainMeta {
  key: Domain;
  label: string;
  labelHi: string;
  icon: LucideIcon;
  /** Short, plain-language framing of the domain (UI copy, not legal advice). */
  blurb: string;
  /** Example situation in the user's own words (sample input, not a legal claim). */
  example: string;
  exampleHi: string;
}

export const DOMAINS: Record<Domain, DomainMeta> = {
  consumer: {
    key: "consumer",
    label: "Consumer",
    labelHi: "उपभोक्ता",
    icon: ShoppingBag,
    blurb: "Defective products, refunds, service or billing problems.",
    example:
      "I ordered a phone online for ₹18,000. It arrived damaged and the seller is refusing to refund or replace it.",
    exampleHi:
      "मैंने ऑनलाइन ₹18,000 का फ़ोन मंगवाया। वह टूटा हुआ आया और विक्रेता रिफ़ंड या बदलने से मना कर रहा है।",
  },
  labor: {
    key: "labor",
    label: "Work & Salary",
    labelHi: "नौकरी और वेतन",
    icon: Briefcase,
    blurb: "Unpaid salary, wrongful termination, workplace issues.",
    example:
      "My employer has not paid my salary for the last two months and now says I am being removed without notice.",
    exampleHi:
      "मेरे नियोक्ता ने पिछले दो महीने का वेतन नहीं दिया और अब बिना सूचना के मुझे निकाल रहे हैं।",
  },
  tenant: {
    key: "tenant",
    label: "Rent & Tenant",
    labelHi: "किराया और किरायेदारी",
    icon: KeyRound,
    blurb: "Deposits, eviction, rent disputes with a landlord.",
    example:
      "My landlord has not returned my ₹20,000 security deposit even though I moved out two months ago.",
    exampleHi:
      "मैं दो महीने पहले घर छोड़ चुका/चुकी हूँ फिर भी मकान मालिक ने मेरी ₹20,000 सिक्योरिटी वापस नहीं की।",
  },
  cyber: {
    key: "cyber",
    label: "Cyber Fraud",
    labelHi: "साइबर धोखाधड़ी",
    icon: ShieldAlert,
    blurb: "Online fraud, unauthorized transactions, digital scams.",
    example:
      "₹45,000 was debited from my bank account through a transaction I never authorized.",
    exampleHi:
      "मेरे बैंक खाते से ₹45,000 एक ऐसे लेन-देन से कट गए जिसकी मैंने कभी अनुमति नहीं दी।",
  },
  criminal: {
    key: "criminal",
    label: "Safety & Offences",
    labelHi: "सुरक्षा और अपराध",
    icon: Gavel,
    blurb: "Threats, harassment, theft, and other offences.",
    example:
      "Someone is repeatedly threatening me over the phone and I am afraid for my safety.",
    exampleHi:
      "कोई व्यक्ति बार-बार फ़ोन पर मुझे धमकी दे रहा है और मुझे अपनी सुरक्षा की चिंता है।",
  },
  general: {
    key: "general",
    label: "Something else",
    labelHi: "कुछ और",
    icon: Scale,
    blurb: "Not sure which category fits? Start here.",
    example: "I have a legal problem but I am not sure which law applies to it.",
    exampleHi: "मेरे साथ एक कानूनी समस्या है पर मुझे नहीं पता कौन सा कानून लागू होता है।",
  },
};

/** The four example chips shown under the input (Part 6). */
export const EXAMPLE_DOMAINS: Domain[] = ["consumer", "labor", "tenant", "cyber"];

/* ------------------------------------------------------------------ *
 * Navigation / Information architecture (Part 5)
 * ------------------------------------------------------------------ */
export interface NavItem {
  to: string;
  label: string;
  labelHi: string;
  icon: LucideIcon;
  end?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Legal Assistant", labelHi: "कानूनी सहायक", icon: Sparkles, end: true },
  { to: "/cases", label: "My Cases", labelHi: "मेरे मामले", icon: FolderClosed },
  { to: "/documents", label: "My Documents", labelHi: "मेरे दस्तावेज़", icon: FileText },
  { to: "/how-it-works", label: "How It Works", labelHi: "यह कैसे काम करता है", icon: Compass },
  { to: "/about", label: "About", labelHi: "परिचय", icon: Info },
];

/* ------------------------------------------------------------------ *
 * Case pipeline (Part 8) — the calm progress "spine"
 * ------------------------------------------------------------------ */
export type PipelineStepId =
  | "situation"
  | "facts"
  | "law"
  | "rights"
  | "evidence"
  | "action"
  | "document";

export interface PipelineStep {
  id: PipelineStepId;
  label: string;
  labelHi: string;
  description?: string;
  descriptionHi?: string;
}

export const PIPELINE_STEPS: PipelineStep[] = [
  { id: "situation", label: "Situation", labelHi: "स्थिति" },
  { id: "facts", label: "Facts", labelHi: "तथ्य" },
  { id: "law", label: "Law", labelHi: "कानून" },
  { id: "rights", label: "Rights", labelHi: "अधिकार" },
  { id: "evidence", label: "Evidence", labelHi: "साक्ष्य" },
  { id: "action", label: "Action", labelHi: "कदम" },
  { id: "document", label: "Document", labelHi: "दस्तावेज़" },
];

/* ------------------------------------------------------------------ *
 * Geographic options for state clarification (not legal content)
 * ------------------------------------------------------------------ */
export const INDIAN_STATES: string[] = [
  "Delhi",
  "Maharashtra",
  "Karnataka",
  "Tamil Nadu",
  "Uttar Pradesh",
  "Gujarat",
  "West Bengal",
  "Rajasthan",
  "Telangana",
  "Kerala",
  "Punjab",
  "Haryana",
  "Bihar",
  "Madhya Pradesh",
  "Other",
];

/* ------------------------------------------------------------------ *
 * Document types offered in the Document Center (Part 17)
 * ------------------------------------------------------------------ */
export interface DocTypeMeta {
  type: string;
  label: string;
  labelHi: string;
  description: string;
  descriptionHi: string;
  domains: Domain[];
}

export const DOCUMENT_TYPES: DocTypeMeta[] = [
  {
    type: "legal_notice",
    label: "Legal Notice",
    labelHi: "कानूनी नोटिस",
    description: "A formal written notice to the other party stating your grievance and demand.",
    descriptionHi: "आपकी शिकायत और माँग बताने वाला दूसरे पक्ष को भेजा जाने वाला औपचारिक लिखित नोटिस।",
    domains: ["consumer", "labor", "tenant", "general"],
  },
  {
    type: "consumer_complaint",
    label: "Consumer Complaint",
    labelHi: "उपभोक्ता शिकायत",
    description: "A structured complaint for a consumer dispute forum.",
    descriptionHi: "उपभोक्ता विवाद मंच के लिए व्यवस्थित शिकायत।",
    domains: ["consumer"],
  },
  {
    type: "labor_complaint",
    label: "Labour Complaint",
    labelHi: "श्रम शिकायत",
    description: "A complaint regarding unpaid wages or workplace grievances.",
    descriptionHi: "बकाया वेतन या कार्यस्थल की समस्या से जुड़ी शिकायत।",
    domains: ["labor"],
  },
  {
    type: "tenant_notice",
    label: "Tenant Notice",
    labelHi: "किरायेदार नोटिस",
    description: "A notice to a landlord regarding deposit, repairs, or tenancy terms.",
    descriptionHi: "जमा राशि, मरम्मत या किरायेदारी की शर्तों के बारे में मकान मालिक को नोटिस।",
    domains: ["tenant"],
  },
  {
    type: "complaint",
    label: "General Complaint",
    labelHi: "सामान्य शिकायत",
    description: "A general-purpose complaint draft grounded in your case.",
    descriptionHi: "आपके मामले पर आधारित सामान्य उपयोग की शिकायत का ड्राफ्ट।",
    domains: ["cyber", "criminal", "general"],
  },
];

export const PRIVACY_REMINDER =
  "Don't enter passwords, OTPs, PINs, or unnecessary sensitive information.";

export const GLOBAL_DISCLAIMER =
  "LegalAId provides general legal information grounded in verified sources — not legal advice. For decisions about your specific situation, consult a licensed advocate.";
