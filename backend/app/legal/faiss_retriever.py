"""
Embedding Service and FAISS Retriever for LegalAId.
Provides dense embeddings with SentenceTransformers and FAISS vector index search.
Tracks index versioning, dimension, and synchronization status.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False


class EmbeddingService:

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384
        self.model = SentenceTransformer(model_name) if (SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer) else None

    def embed(self, texts: list[str]) -> np.ndarray:
        if self.model is not None:
            vectors = self.model.encode(
                texts,
                normalize_embeddings=True,
            )
            return np.asarray(vectors, dtype=np.float32)
        
        # Hash vector fallback if sentence-transformers is offline
        vecs = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, txt in enumerate(texts):
            h = abs(hash(txt))
            idx = h % self.dimension
            vecs[i, idx] = 1.0
        return vecs

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]


class FaissRetriever:

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension) if (FAISS_AVAILABLE and faiss) else None
        self.record_ids: list[int] = []
        self.stored_embeddings: list[np.ndarray] = []
        
        # Vector index version metadata
        self.corpus_version = "1.0.0"
        self.embedding_model_version = "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_dimension = dimension
        self.index_version = "v1"
        self.indexed_at = datetime.utcnow().isoformat()

    def add(self, embeddings, record_ids):
        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )
        if self.index is not None:
            self.index.add(embeddings)
        else:
            self.stored_embeddings.extend(embeddings)
        self.record_ids.extend(record_ids)
        self.indexed_at = datetime.utcnow().isoformat()

    def search(self, query_embedding, k=10):
        query_embedding = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        results = []
        if self.index is not None and len(self.record_ids) > 0:
            scores, indices = self.index.search(
                query_embedding,
                min(k, len(self.record_ids)),
            )
            for score, index in zip(scores[0], indices[0]):
                if index < 0 or index >= len(self.record_ids):
                    continue
                results.append({
                    "record_id": self.record_ids[index],
                    "score": float(score),
                })
        elif self.stored_embeddings:
            matrix = np.asarray(self.stored_embeddings, dtype=np.float32)
            sims = np.dot(matrix, query_embedding[0])
            top_k = min(k, len(sims))
            top_indices = np.argsort(-sims)[:top_k]
            for idx in top_indices:
                results.append({
                    "record_id": self.record_ids[idx],
                    "score": float(sims[idx]),
                })
        return results

    def get_index_health(self, db_section_count: int) -> Dict[str, Any]:
        vector_count = len(self.record_ids)
        
        if vector_count == 0:
            vector_state = "uninitialized"
            in_sync = False
            status_msg = "UNINITIALIZED: Vector index not yet built (BM25 fallback active)"
        elif vector_count == db_section_count:
            vector_state = "ready"
            in_sync = True
            status_msg = f"SYNCHRONIZED ({vector_count} vectors)"
        else:
            vector_state = "out_of_sync"
            in_sync = False
            status_msg = f"WARNING: Vector index out of sync ({vector_count} vectors vs {db_section_count} db records)"
        
        return {
            "vector_count": vector_count,
            "db_section_count": db_section_count,
            "in_sync": in_sync,
            "vector_state": vector_state,
            "status": status_msg,
            "corpus_version": self.corpus_version,
            "embedding_model_version": self.embedding_model_version,
            "embedding_dimension": self.embedding_dimension,
            "index_version": self.index_version,
            "indexed_at": self.indexed_at,
            "faiss_available": FAISS_AVAILABLE,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE
        }


# Singleton vector retriever
vector_retriever = FaissRetriever()
