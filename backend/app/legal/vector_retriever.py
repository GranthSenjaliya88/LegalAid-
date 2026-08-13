"""
Phase 9 — Lightweight TF-IDF / Vector Retrieval Engine.
Provides cosine-similarity vector scoring over legal section texts to enable dense semantic matching fused with BM25 (FTS5).
"""

import math
import re
from typing import List, Dict, Tuple, Any


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lowercase terms."""
    return re.findall(r"\w+", text.lower())


def compute_tf_idf_vector(tokens: List[str], df_dict: Dict[str, int], total_docs: int) -> Dict[str, float]:
    """Compute TF-IDF weight vector for a list of tokens."""
    if not tokens:
        return {}
    tf_dict: Dict[str, int] = {}
    for t in tokens:
        tf_dict[t] = tf_dict.get(t, 0) + 1

    vec: Dict[str, float] = {}
    doc_len = len(tokens)
    for term, count in tf_dict.items():
        tf = count / doc_len
        df = df_dict.get(term, 1)
        idf = math.log((total_docs + 1.0) / (df + 1.0)) + 1.0
        vec[term] = tf * idf

    # L2 normalize
    norm = math.sqrt(sum(val * val for val in vec.values()))
    if norm > 0:
        for k in vec:
            vec[k] /= norm
    return vec


def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two normalized sparse vectors."""
    dot_product = 0.0
    for term, val in vec1.items():
        if term in vec2:
            dot_product += val * vec2[term]
    return dot_product


def rank_sections_by_vector(
    query_text: str,
    sections: List[Dict[str, Any]]
) -> List[Tuple[int, float]]:
    """
    Rank candidate sections by cosine similarity using TF-IDF vector weights.
    Returns list of (section_id, vector_similarity_score).
    """
    if not query_text or not sections:
        return []

    total_docs = len(sections)
    df_dict: Dict[str, int] = {}

    doc_tokens_map: Dict[int, List[str]] = {}
    for sec in sections:
        sec_id = sec["id"]
        combined_text = (
            f"{sec.get('title', '')} {sec.get('text', '')} {sec.get('domain', '')} "
            f"{sec.get('subdomain', '')} {sec.get('keywords', '')}"
        )
        tokens = _tokenize(combined_text)
        doc_tokens_map[sec_id] = tokens
        unique_terms = set(tokens)
        for t in unique_terms:
            df_dict[t] = df_dict.get(t, 0) + 1

    query_tokens = _tokenize(query_text)
    query_vec = compute_tf_idf_vector(query_tokens, df_dict, total_docs)

    scores: List[Tuple[int, float]] = []
    for sec in sections:
        sec_id = sec["id"]
        doc_tokens = doc_tokens_map[sec_id]
        doc_vec = compute_tf_idf_vector(doc_tokens, df_dict, total_docs)
        sim = cosine_similarity(query_vec, doc_vec)
        scores.append((sec_id, round(sim, 4)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
