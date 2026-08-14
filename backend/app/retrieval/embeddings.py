"""
Dense Vector Embeddings Search Module.
"""

from typing import List, Dict, Tuple, Any
from app.legal.faiss_vector_retriever import vector_index
from app.legal.vector_retriever import rank_sections_by_vector, compute_tf_idf_vector, cosine_similarity


def search_vector_embeddings(query_text: str, candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Tuple[int, float]]:
    """Search dense FAISS / TF-IDF vector embeddings."""
    return vector_index.search(query_text, candidates, top_k=top_k)
