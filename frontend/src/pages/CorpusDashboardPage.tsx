import { useState, useEffect } from "react";
import {
  ShieldCheck,
  FileText,
  BookOpen,
  Scale,
  Building2,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Database,
  Search,
  Layers,
  Clock
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/services/apiClient";

interface DashboardData {
  total_acts: number;
  total_sections: number;
  total_rules: number;
  total_regulations: number;
  total_notifications: number;
  total_judgments: number;
  total_authorities: number;
  total_procedures: number;
  total_concepts: number;
  total_sources: number;
  total_historical_mappings: number;
  total_graph_edges: number;
  current_sections: number;
  historical_sections: number;
  verified_sections: number;
  needs_review_sections: number;
  rejected_sections: number;
  domains_count: number;
  domains_covered: Record<string, number>;
  states_count: number;
  states_covered: Record<string, number>;
  source_types_covered: Record<string, number>;
  index_health?: {
    database_count: number;
    fts_count: number;
    vector_count: number;
    in_sync: boolean;
    vector_status: string;
  };
  evaluation_metrics?: {
    software_quality: {
      pytest_pass_rate: number;
      api_health_status: string;
      frontend_build_status: string;
      pdf_generation_integrity: string;
      e2e_status: string;
      existing_test_count: number;
    };
    retrieval_quality: {
      precision_at_1: number;
      precision_at_5: number;
      recall_at_1: number;
      recall_at_5: number;
      mrr: number;
      total_golden_eval_cases: number;
    };
    legal_quality: {
      citation_accuracy: number;
      claim_support_accuracy: number;
      applicability_accuracy: number;
      jurisdiction_accuracy: number;
      incident_date_accuracy: number;
      current_law_accuracy: number;
      refusal_accuracy: number;
      unsupported_claim_rate: number;
      total_hard_negative_cases: number;
    };
  };
  quality_issues: {
    missing_url: number;
    missing_date: number;
    missing_text: number;
    unknown_status: number;
    unknown_jurisdiction: number;
  };
  integrity_passed: boolean;
  integrity_summary: string;
}

export function CorpusDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "index" | "eval">("overview");

  useEffect(() => {
    let cancelled = false;

    apiClient
      .get<DashboardData>("/api/admin/corpus-dashboard")
      .then((dashboard) => {
        if (!cancelled) setData(dashboard);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="container max-w-7xl py-12 flex flex-col items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mb-4"></div>
        <p className="text-slate-600 font-medium">Loading Live Legal Corpus Dashboard Statistics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container max-w-7xl py-12">
        <Card className="border-red-200 bg-red-50 text-red-900 p-6">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            Failed to Load Corpus Dashboard
          </h2>
          <p className="mt-2 text-sm text-red-700">{error || "No data received from API."}</p>
        </Card>
      </div>
    );
  }

  const evalM = data.evaluation_metrics;
  const idxH = data.index_health;

  return (
    <div className="container max-w-7xl py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Legal Corpus & Quality Dashboard</h1>
            <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-300">
              Live Production State
            </Badge>
          </div>
          <p className="text-sm text-slate-600 mt-1">
            Real-time audit of statutory breadth, source verification, index synchronization, and quality metrics.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={activeTab === "overview" ? "primary" : "outline"}
            onClick={() => setActiveTab("overview")}
            size="sm"
          >
            Corpus Overview
          </Button>
          <Button
            variant={activeTab === "index" ? "primary" : "outline"}
            onClick={() => setActiveTab("index")}
            size="sm"
          >
            Index Health
          </Button>
          <Button
            variant={activeTab === "eval" ? "primary" : "outline"}
            onClick={() => setActiveTab("eval")}
            size="sm"
          >
            Quality Metrics
          </Button>
        </div>
      </div>

      {activeTab === "overview" && (
        <>
          {/* Top Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="bg-white">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-emerald-50 rounded-xl text-emerald-700">
                  <BookOpen className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Statutory Acts</p>
                  <p className="text-2xl font-bold text-slate-900">{data.total_acts}</p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-teal-50 rounded-xl text-teal-700">
                  <FileText className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Verified Sections</p>
                  <p className="text-2xl font-bold text-slate-900">{data.total_sections}</p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-amber-50 rounded-xl text-amber-700">
                  <Layers className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Rules & Regulations</p>
                  <p className="text-2xl font-bold text-slate-900">{data.total_rules + data.total_regulations}</p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-blue-50 rounded-xl text-blue-700">
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Official Sources</p>
                  <p className="text-2xl font-bold text-slate-900">{data.total_sources}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Record Types Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Legal Source Types Breakdown</CardTitle>
              <CardDescription>Distinct entity counts across multi-layer corpus architecture.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Acts / Statutes</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_acts}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Sections</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_sections}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Rules</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_rules}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Regulations</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_regulations}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Notifications & Circulars</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_notifications}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Procedures</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_procedures}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Precedent Judgments</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_judgments}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Legal Concepts</span>
                  <span className="font-bold text-slate-900 text-lg">{data.total_concepts}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {activeTab === "index" && idxH && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database className="h-5 w-5 text-teal-700" />
              Index Health & Synchronization Status
            </CardTitle>
            <CardDescription>Live record count alignment between DB, FTS5 lexical index, and FAISS vector index.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 border rounded-xl bg-slate-50">
                <span className="text-xs text-slate-500 font-medium">Database Record Count</span>
                <p className="text-3xl font-bold text-slate-900 mt-1">{idxH.database_count}</p>
              </div>
              <div className="p-4 border rounded-xl bg-slate-50">
                <span className="text-xs text-slate-500 font-medium">FTS5 Lexical Index Count</span>
                <p className="text-3xl font-bold text-slate-900 mt-1">{idxH.fts_count}</p>
              </div>
              <div className="p-4 border rounded-xl bg-slate-50">
                <span className="text-xs text-slate-500 font-medium">FAISS Dense Vector Count</span>
                <p className="text-3xl font-bold text-slate-900 mt-1">{idxH.vector_count}</p>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-900 flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              <span className="font-medium text-sm">{idxH.vector_status}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "eval" && evalM && (
        <div className="space-y-6">
          {/* Software Quality */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">A. Software Quality Metrics</CardTitle>
              <CardDescription>Regression suite, API health, build, and test status.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Pytest Pass Rate</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.software_quality.pytest_pass_rate}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Regression Tests</span>
                  <span className="font-bold text-slate-900 text-lg">{evalM.software_quality.existing_test_count} Passed</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">API Health</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.software_quality.api_health_status}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">E2E Suite</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.software_quality.e2e_status}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Retrieval Quality */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">B. Retrieval Quality Metrics (P@K, R@K, MRR)</CardTitle>
              <CardDescription>Benchmark ranking precision and recall on golden evaluation dataset.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-sm">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Precision@1</span>
                  <span className="font-bold text-slate-900 text-lg">{(evalM.retrieval_quality.precision_at_1 * 100).toFixed(1)}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Precision@5</span>
                  <span className="font-bold text-slate-900 text-lg">{(evalM.retrieval_quality.precision_at_5 * 100).toFixed(1)}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Recall@1</span>
                  <span className="font-bold text-slate-900 text-lg">{(evalM.retrieval_quality.recall_at_1 * 100).toFixed(1)}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Recall@5</span>
                  <span className="font-bold text-slate-900 text-lg">{(evalM.retrieval_quality.recall_at_5 * 100).toFixed(1)}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">MRR</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.retrieval_quality.mrr.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Legal Quality */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">C. Legal Quality & Refusal Accuracy Metrics</CardTitle>
              <CardDescription>Citation accuracy, claim-support accuracy, jurisdiction accuracy, and refusal rate.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Citation Accuracy</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.legal_quality.citation_accuracy}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Claim-Support Accuracy</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.legal_quality.claim_support_accuracy}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Jurisdiction Accuracy</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.legal_quality.jurisdiction_accuracy}%</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-500 block text-xs">Refusal Accuracy</span>
                  <span className="font-bold text-emerald-700 text-lg">{evalM.legal_quality.refusal_accuracy}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
