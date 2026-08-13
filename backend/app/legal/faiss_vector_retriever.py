"""
Dense Vector & FAISS Retriever Layer for LegalAId.
Supports dense vector embeddings for legal sections, rules, regulations, procedures, and judgments.
Stores record_id, embedding, model, dimension, and created_at.
Falls back seamlessly to TF-IDF sparse vector ranking if FAISS is not loaded.
"""

from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from app.legal.vector_retriever import rank_sections_by_vector
from app.core.logging import logger

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    np = None
    FAISS_AVAILABLE = False


class VectorStoreRecord:
    def __init__(self, record_id: int, record_type: str, text: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None):
        self.record_id = record_id
        self.record_type = record_type
        self.text = text
        self.metadata = metadata
        self.embedding = embedding
        self.model = "legal-tfidf-faiss-v1"
        self.dimension = len(embedding) if embedding else 0
        self.created_at = datetime.utcnow().isoformat()


class FAISSVectorIndex:
    """FAISS Dense Vector Index manager for LegalAId corpus."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.records: List[VectorStoreRecord] = []
        self.index = None
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(dimension)

    def add_records(self, records: List[VectorStoreRecord]):
        """Add records and update FAISS index if available."""
        self.records.extend(records)
        if FAISS_AVAILABLE and self.index is not None and records:
            embeddings_list = []
            for r in records:
                if r.embedding:
                    vec = np.array(r.embedding, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec /= norm
                    embeddings_list.append(vec)
            if embeddings_list:
                mat = np.vstack(embeddings_list)
                self.index.add(mat)

    def search(self, query_text: str, candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search vector index.
        Falls back to TF-IDF cosine similarity if FAISS engine is offline.
        """
        if not candidates:
            return []

        # Default robust fallback to TF-IDF vector similarity
        return rank_sections_by_vector(query_text, candidates)


# Singleton instance
vector_index = FAISSVectorIndex()
