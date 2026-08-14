"""
LegalAId — Wall-Clock Latency Benchmark Engine.
Measures real performance for DB retrieval, classification, audit, document drafting, and PDF generation.
"""

import time
import statistics
import json
from app.db.database import get_connection, SessionLocal
from app.legal.corpus_search import search_corpus
from app.services.classifier import classify_case_service
from app.services.retriever import retrieve_legal_sections
from app.services.explainer import explain_rights_service
from app.services.pdf_generator import generate_pdf_bytes


def benchmark_pipeline():
    print("=" * 80)
    print("LEGALAID — REAL WALL-CLOCK LATENCY BREAKDOWN")
    print("=" * 80)

    sample_query = "My landlord in Karnataka has not returned my security deposit of 25000."

    timings = {
        "db_query_ms": [],
        "classification_ms": [],
        "corpus_retrieval_ms": [],
        "rights_explanation_ms": [],
        "pdf_generation_ms": [],
        "total_pipeline_ms": []
    }

    # Warmup
    classify_case_service(sample_query)

    iterations = 20
    for _ in range(iterations):
        t_total_start = time.perf_counter()

        # 1. DB Query test
        t0 = time.perf_counter()
        conn = get_connection()
        cnt = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
        conn.close()
        timings["db_query_ms"].append((time.perf_counter() - t0) * 1000)

        # 2. Classification
        t0 = time.perf_counter()
        c = classify_case_service(sample_query)
        timings["classification_ms"].append((time.perf_counter() - t0) * 1000)

        # 3. Corpus Retrieval
        t0 = time.perf_counter()
        r = retrieve_legal_sections(domain=c.domain, facts=c.facts.model_dump())
        timings["corpus_retrieval_ms"].append((time.perf_counter() - t0) * 1000)

        # 4. Rights Explanation
        t0 = time.perf_counter()
        e = explain_rights_service(r.matches, c.facts.model_dump())
        timings["rights_explanation_ms"].append((time.perf_counter() - t0) * 1000)

        # 5. PDF Generation
        t0 = time.perf_counter()
        doc_data = {
            "document_id": "doc-test-12345",
            "title": "LEGAL NOTICE FOR SECURITY DEPOSIT REFUND",
            "sections": [
                {"id": "header", "title": "Parties & Header", "content": "FROM: Aggrieved Tenant\nTO: Landlord\nAMOUNT: ₹25,000"},
                {"id": "demands", "title": "Legal Demands", "content": "Refund ₹25,000 security deposit within 15 days under Model Tenancy Act, 2021."}
            ],
            "disclaimer": "MANDATORY LEGAL DISCLAIMER: Generated for informational purposes."
        }
        pdf_bytes = generate_pdf_bytes(doc_data)
        timings["pdf_generation_ms"].append((time.perf_counter() - t0) * 1000)

        timings["total_pipeline_ms"].append((time.perf_counter() - t_total_start) * 1000)

    metrics = {}
    for stage, vals in timings.items():
        sorted_vals = sorted(vals)
        p50 = statistics.median(sorted_vals)
        p95 = sorted_vals[int(len(sorted_vals) * 0.95)]
        avg = statistics.mean(sorted_vals)
        metrics[stage] = {
            "avg_ms": round(avg, 2),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2)
        }

    print(json.dumps(metrics, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    benchmark_pipeline()
