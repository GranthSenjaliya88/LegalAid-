"""
Legal Search Engine Abstraction Layer.
Decouples business logic from specific database search implementations (SQLite FTS5 vs PostgreSQL pgvector).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np


class LegalSearchEngine(ABC):
    """Abstract interface for legal search engines."""

    @abstractmethod
    def search_bm25(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Perform full-text lexical search using BM25 scoring."""
        pass

    @abstractmethod
    def search_vector(self, query_vector: np.ndarray, limit: int = 20) -> List[Dict[str, Any]]:
        """Perform dense vector similarity search."""
        pass

    @abstractmethod
    def search_hybrid(
        self,
        query: str,
        query_vector: Optional[np.ndarray] = None,
        domain: Optional[str] = None,
        limit: int = 20,
        k_fusion: int = 60
    ) -> List[Dict[str, Any]]:
        """Perform hybrid fusion search combining lexical and vector results."""
        pass


class SQLiteSearchEngine(LegalSearchEngine):
    """SQLite implementation using FTS5 + FAISS vector index."""

    def __init__(self, db_session=None):
        self.db_session = db_session

    def search_bm25(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        from app.legal.corpus_search import search_bm25
        if self.db_session:
            return search_bm25(self.db_session, query, limit=limit)
        return []

    def search_vector(self, query_vector: np.ndarray, limit: int = 20) -> List[Dict[str, Any]]:
        from app.legal.faiss_retriever import FaissRetriever
        retriever = FaissRetriever()
        if query_vector is not None:
            return retriever.search(query_vector, k=limit)
        return []

    def search_hybrid(
        self,
        query: str,
        query_vector: Optional[np.ndarray] = None,
        domain: Optional[str] = None,
        limit: int = 20,
        k_fusion: int = 60
    ) -> List[Dict[str, Any]]:
        from app.legal.corpus_search import reciprocal_rank_fusion
        bm25_res = self.search_bm25(query, domain=domain, limit=limit)
        vec_res = self.search_vector(query_vector, limit=limit) if query_vector is not None else []
        return reciprocal_rank_fusion(bm25_res, vec_res, k=k_fusion)


class PostgresSearchEngine(LegalSearchEngine):
    """PostgreSQL implementation using tsvector + pgvector extension."""

    def __init__(self, db_session=None):
        self.db_session = db_session

    def search_bm25(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        # Placeholder PostgreSQL full-text search query (tsvector / tsquery)
        return []

    def search_vector(self, query_vector: np.ndarray, limit: int = 20) -> List[Dict[str, Any]]:
        # Placeholder PostgreSQL pgvector cosine similarity search
        return []

    def search_hybrid(
        self,
        query: str,
        query_vector: Optional[np.ndarray] = None,
        domain: Optional[str] = None,
        limit: int = 20,
        k_fusion: int = 60
    ) -> List[Dict[str, Any]]:
        from app.legal.corpus_search import reciprocal_rank_fusion
        bm25_res = self.search_bm25(query, domain=domain, limit=limit)
        vec_res = self.search_vector(query_vector, limit=limit) if query_vector is not None else []
        return reciprocal_rank_fusion(bm25_res, vec_res, k=k_fusion)
