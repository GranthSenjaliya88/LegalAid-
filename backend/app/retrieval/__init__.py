"""
Retrieval Package for LegalAId.
Provides BM25 full-text search, dense embeddings vector search, and hybrid result fusion.
"""
from app.legal.corpus_search import search_corpus
from app.legal.vector_retriever import rank_sections_by_vector
from app.legal.faiss_vector_retriever import vector_index
