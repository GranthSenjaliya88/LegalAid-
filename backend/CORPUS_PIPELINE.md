# Legal corpus expansion and accuracy pipeline

LegalAId treats corpus growth and legal accuracy as separate gates. More text is
not considered better unless every provision is traceable to an official source,
versioned, current, and covered by retrieval tests.

## Import complete acts from India Code

The curated files in `data/statutes/` provide the trusted act metadata and domain
mapping. The bulk importer discovers the complete section list on India Code,
downloads the official text, stores source URLs and SHA-256 hashes, snapshots the
normalized result, and upserts it through the only authorized loader.

```powershell
$env:PYTHONPATH="backend"

# Count sections before downloading text
python backend/scripts/ingest_official_corpus.py --discover-only

# Import a focused domain first
python backend/scripts/ingest_official_corpus.py --domain consumer --workers 4

# Import every curated India Code act
python backend/scripts/ingest_official_corpus.py --workers 4
```

Generated snapshots are stored under `backend/data/official_snapshots/` and are
committed as versioned production assets. At startup, the application loads these
local snapshots without making network requests, so an ephemeral Render instance
receives the complete verified corpus deterministically. Each importer run is
recorded in `ingestion_runs`; failures and questionable records go to
`ingestion_rejections`, while changed provisions are preserved in
`section_versions` before replacement.

## Accuracy rules

- Only allow-listed government hosts can be marked `VERIFIED`.
- Verified records require an official URL and a verification date.
- Retrieval excludes pending, rejected, repealed, and source-less provisions.
- Official title/text wins when curated metadata conflicts with India Code.
- Statutory text is never generated or completed by an LLM.
- A larger corpus must pass the golden retrieval and refusal benchmarks.

Run the quality report after every import:

```powershell
python backend/scripts/evaluate_corpus_quality.py
python -m pytest backend/tests -q
```

For long-term production writes and scheduled ingestion, use a managed database.
The bundled snapshots make the read corpus reproducible on Render's ephemeral
filesystem; SQLite/FTS5 remains suitable for this read-heavy corpus and tens of
thousands of provisions.
