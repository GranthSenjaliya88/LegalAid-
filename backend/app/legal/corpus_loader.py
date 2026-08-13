"""
Legal corpus loader.
Ingests human-verified statute JSON files into LegalAct and LegalSection tables.
"""

from corpus.loader import load_file, load_all, ALLOWED_DOMAINS, STATUTES_DIR

__all__ = ["load_file", "load_all", "ALLOWED_DOMAINS", "STATUTES_DIR"]
